from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID
from ..models.message_models import ProcessedMessage
from .repositories.message_repository import MessageRepository
from .repositories.node_repository import NodeRepository
from .repositories.edge_repository import EdgeRepository
import logging

class GraphStore:
    """Orchestrates all database operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.message_repo = MessageRepository(db)
        self.node_repo = NodeRepository(db)
        self.edge_repo = EdgeRepository(db)
        self.logger = logging.getLogger(__name__)
    
    def store_processed_message(self, processed: ProcessedMessage) -> Dict[str, Any]:
        """Store a processed message and all related nodes/edges"""
        result = {
            'message_id': None,
            'nodes_created': 0,
            'edges_created': 0,
            'relationships': []
        }
        
        try:
            # 1. Store message
            message = self.message_repo.create(processed)
            result['message_id'] = str(message.message_id)
            self.logger.info(f"Stored message with ID: {message.message_id}")
            
            # 2. Store entities as nodes
            entity_nodes = []
            for entity in processed.entities:
                node = self.node_repo.upsert_entity_node(entity, message.message_id)
                if node:
                    entity_nodes.append(node)
                    result['nodes_created'] += 1
                    self.logger.debug(f"Upserted entity node: {entity.text}")
            
            # 3. Store intent as node
            intent_node = self.node_repo.upsert_intent_node(processed.intent, message.message_id)
            if intent_node:
                result['nodes_created'] += 1
                result['relationships'].append({
                    'type': 'intent',
                    'node_id': str(intent_node.node_id),
                    'value': processed.intent.primary_intent
                })
                self.logger.debug(f"Upserted intent node: {processed.intent.primary_intent}")
            
            # 4. Store emotions as nodes
            emotion_nodes = []
            emotion_dict = processed.emotions.to_dict()
            for emotion_name, score in emotion_dict.items():
                if score > 0.1:  # Only store significant emotions
                    node = self.node_repo.upsert_emotion_node(emotion_name, score, message.message_id)
                    if node:
                        emotion_nodes.append(node)
                        result['nodes_created'] += 1
                        result['relationships'].append({
                            'type': 'emotion',
                            'node_id': str(node.node_id),
                            'value': emotion_name,
                            'score': score
                        })
                        self.logger.debug(f"Upserted emotion node: {emotion_name} ({score:.2f})")
            
            # 5. Create relationships (edges)
            
            # Link message to intent
            if intent_node:
                edge = self.edge_repo.create_or_update(
                    source_id=message.message_id,
                    target_id=intent_node.node_id,
                    edge_type='HAS_INTENT',
                    properties={'confidence': processed.intent.confidence}
                )
                if edge:
                    result['edges_created'] += 1
            
            # Link intent to entities
            for entity_node in entity_nodes:
                edge = self.edge_repo.create_or_update(
                    source_id=intent_node.node_id if intent_node else message.message_id,
                    target_id=entity_node.node_id,
                    edge_type='MENTIONS',
                    properties={
                        'entity_type': next((e.label for e in processed.entities if e.text == entity_node.node_label), 'unknown'),
                        'context': processed.raw_text[:100]  # Store context snippet
                    }
                )
                if edge:
                    result['edges_created'] += 1
            
            # Link emotions to message
            for emotion_node in emotion_nodes:
                edge = self.edge_repo.create_or_update(
                    source_id=message.message_id,
                    target_id=emotion_node.node_id,
                    edge_type='EXPRESSES',
                    properties={'score': emotion_dict.get(emotion_node.node_label, 0)}
                )
                if edge:
                    result['edges_created'] += 1
            
            # Link entities to each other if they appear in same message (co-occurrence)
            for i, entity1 in enumerate(entity_nodes):
                for entity2 in entity_nodes[i+1:]:
                    edge = self.edge_repo.create_or_update(
                        source_id=entity1.node_id,
                        target_id=entity2.node_id,
                        edge_type='CO_OCCURS_WITH',
                        properties={'message_id': str(message.message_id)}
                    )
                    if edge:
                        result['edges_created'] += 1
            
            self.db.commit()
            self.logger.info(f"Successfully stored message with {result['nodes_created']} nodes and {result['edges_created']} edges")
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error storing message: {e}")
            raise
        
        return result
    
    def get_message_graph(self, message_id: UUID) -> Dict[str, Any]:
        """Retrieve the complete graph for a specific message"""
        try:
            # Get the message
            message = self.message_repo.get_by_id(message_id)
            if not message:
                return {'error': 'Message not found'}
            
            # Get all nodes linked to this message
            nodes = self.db.execute("""
                SELECT n.* 
                FROM nodes n
                JOIN message_nodes mn ON n.node_id = mn.node_id
                WHERE mn.message_id = :message_id
            """, {'message_id': message_id}).fetchall()
            
            # Get all edges between these nodes
            edges = self.db.execute("""
                SELECT e.* 
                FROM edges e
                WHERE e.source_node_id IN (
                    SELECT node_id FROM message_nodes WHERE message_id = :message_id
                ) AND e.target_node_id IN (
                    SELECT node_id FROM message_nodes WHERE message_id = :message_id
                )
            """, {'message_id': message_id}).fetchall()
            
            return {
                'message': {
                    'id': str(message.message_id),
                    'text': message.raw_text[:200] + '...' if len(message.raw_text) > 200 else message.raw_text,
                    'processed_at': message.processed_at.isoformat() if message.processed_at else None,
                    'sentiment': message.sentiment,
                    'intent': message.intent
                },
                'nodes': [dict(node) for node in nodes],
                'edges': [dict(edge) for edge in edges]
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving message graph: {e}")
            return {'error': str(e)}
    
    def get_user_graph(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get the complete graph for a user across all their messages"""
        try:
            # Get all messages for user
            messages = self.message_repo.get_by_user(user_id, limit)
            message_ids = [m.message_id for m in messages]
            
            if not message_ids:
                return {'error': 'No messages found for user'}
            
            # Get all nodes from these messages
            nodes = self.db.execute("""
                SELECT n.*, COUNT(DISTINCT mn.message_id) as message_count
                FROM nodes n
                JOIN message_nodes mn ON n.node_id = mn.node_id
                WHERE mn.message_id = ANY(:message_ids)
                GROUP BY n.node_id
                ORDER BY message_count DESC
            """, {'message_ids': message_ids}).fetchall()
            
            # Get edges between these nodes
            edges = self.db.execute("""
                SELECT e.*, COUNT(*) as occurrence_count
                FROM edges e
                WHERE e.source_node_id IN (
                    SELECT node_id FROM message_nodes WHERE message_id = ANY(:message_ids)
                ) AND e.target_node_id IN (
                    SELECT node_id FROM message_nodes WHERE message_id = ANY(:message_ids)
                )
                GROUP BY e.edge_id
                ORDER BY occurrence_count DESC
                LIMIT 200
            """, {'message_ids': message_ids}).fetchall()
            
            # Get sentiment trend
            sentiment_trend = [
                {
                    'date': m.processed_at.isoformat() if m.processed_at else None,
                    'sentiment': m.sentiment.get('class') if m.sentiment else 'neutral',
                    'polarity': m.sentiment.get('polarity', 0) if m.sentiment else 0
                }
                for m in messages
            ]
            
            # Get intent distribution
            intent_distribution = {}
            for m in messages:
                if m.intent and m.intent.get('primary_intent'):
                    intent = m.intent['primary_intent']
                    intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
            
            return {
                'user_id': user_id,
                'message_count': len(messages),
                'nodes': [dict(node) for node in nodes],
                'edges': [dict(edge) for edge in edges],
                'analytics': {
                    'sentiment_trend': sentiment_trend,
                    'intent_distribution': intent_distribution,
                    'avg_sentiment': sum(m.sentiment.get('polarity', 0) for m in messages) / len(messages) if messages else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving user graph: {e}")
            return {'error': str(e)}
    
    def get_session_graph(self, session_id: str) -> Dict[str, Any]:
        """Get the graph for a specific session"""
        try:
            messages = self.message_repo.get_by_session(session_id)
            message_ids = [m.message_id for m in messages]
            
            if not message_ids:
                return {'error': 'No messages found for session'}
            
            # Similar to user graph but for session
            nodes = self.db.execute("""
                SELECT n.*, COUNT(DISTINCT mn.message_id) as message_count
                FROM nodes n
                JOIN message_nodes mn ON n.node_id = mn.node_id
                WHERE mn.message_id = ANY(:message_ids)
                GROUP BY n.node_id
                ORDER BY message_count DESC
            """, {'message_ids': message_ids}).fetchall()
            
            return {
                'session_id': session_id,
                'message_count': len(messages),
                'nodes': [dict(node) for node in nodes],
                'messages': [
                    {
                        'id': str(m.message_id),
                        'text': m.raw_text[:100] + '...' if len(m.raw_text) > 100 else m.raw_text,
                        'sentiment': m.sentiment.get('class') if m.sentiment else None,
                        'intent': m.intent.get('primary_intent') if m.intent else None,
                        'processed_at': m.processed_at.isoformat() if m.processed_at else None
                    }
                    for m in messages
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving session graph: {e}")
            return {'error': str(e)}
    
    def get_entity_network(self, entity_type: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get network of entities and their relationships"""
        try:
            query = """
                SELECT 
                    n1.node_label as source_entity,
                    n2.node_label as target_entity,
                    e.edge_type,
                    e.weight,
                    COUNT(DISTINCT mn1.message_id) as co_occurrence_count
                FROM edges e
                JOIN nodes n1 ON e.source_node_id = n1.node_id
                JOIN nodes n2 ON e.target_node_id = n2.node_id
                LEFT JOIN message_nodes mn1 ON n1.node_id = mn1.node_id
                LEFT JOIN message_nodes mn2 ON n2.node_id = mn2.node_id
                WHERE n1.node_type = 'entity' AND n2.node_type = 'entity'
            """
            
            params = {}
            if entity_type:
                query += " AND (n1.properties->>'entity_type' = :entity_type OR n2.properties->>'entity_type' = :entity_type)"
                params['entity_type'] = entity_type
            
            query += " GROUP BY n1.node_label, n2.node_label, e.edge_type, e.weight ORDER BY co_occurrence_count DESC LIMIT :limit"
            params['limit'] = limit
            
            results = self.db.execute(query, params).fetchall()
            
            # Format for network visualization
            nodes = set()
            links = []
            
            for row in results:
                nodes.add(row.source_entity)
                nodes.add(row.target_entity)
                links.append({
                    'source': row.source_entity,
                    'target': row.target_entity,
                    'type': row.edge_type,
                    'weight': row.weight,
                    'co_occurrence': row.co_occurrence_count
                })
            
            return {
                'nodes': list(nodes),
                'links': links,
                'total_relationships': len(links)
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving entity network: {e}")
            return {'error': str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        try:
            stats = self.db.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM messages) as total_messages,
                    (SELECT COUNT(*) FROM nodes) as total_nodes,
                    (SELECT COUNT(*) FROM edges) as total_edges,
                    (SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id IS NOT NULL) as unique_users,
                    (SELECT COUNT(DISTINCT session_id) FROM messages WHERE session_id IS NOT NULL) as unique_sessions,
                    (SELECT jsonb_object_agg(node_type, count) FROM (
                        SELECT node_type, COUNT(*) as count FROM nodes GROUP BY node_type
                    ) t) as nodes_by_type,
                    (SELECT AVG(frequency) FROM nodes) as avg_node_frequency,
                    (SELECT AVG(weight) FROM edges) as avg_edge_weight
            """).fetchone()
            
            return dict(stats) if stats else {}
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Delete data older than specified days"""
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Delete old messages (cascades to message_nodes)
            result = self.db.execute("""
                DELETE FROM messages 
                WHERE processed_at < :cutoff_date
                RETURNING message_id
            """, {'cutoff_date': cutoff_date})
            
            deleted_count = len(result.fetchall())
            
            # Clean up orphaned nodes (nodes with no message links)
            self.db.execute("""
                DELETE FROM nodes n
                WHERE NOT EXISTS (
                    SELECT 1 FROM message_nodes mn WHERE mn.node_id = n.node_id
                )
            """)
            
            self.db.commit()
            self.logger.info(f"Cleaned up {deleted_count} messages older than {days} days")
            return deleted_count
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error during cleanup: {e}")
            return 0