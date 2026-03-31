from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any
from uuid import UUID
from ...models.database_models import Node, MessageNode
from ...models.message_models import Entity, Emotion, Intent

class NodeRepository:
    """Handles node database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def upsert_entity_node(self, entity: Entity, message_id: UUID) -> Node:
        """Upsert an entity node and link to message"""
        # Find or create node
        node = self.db.query(Node).filter(
            Node.node_type == 'entity',
            Node.node_label == entity.text
        ).first()
        
        if node:
            # Update existing node
            node.frequency += 1
            node.last_updated = func.now()
            
            # Update properties with new position
            positions = node.properties.get('positions', [])
            positions.append({'start': entity.start_char, 'end': entity.end_char})
            node.properties['positions'] = positions
        else:
            # Create new node
            node = Node(
                node_type='entity',
                node_label=entity.text,
                properties={
                    'entity_type': entity.label,
                    'description': entity.description,
                    'positions': [{'start': entity.start_char, 'end': entity.end_char}]
                },
                confidence_score=entity.confidence
            )
            self.db.add(node)
            self.db.flush()
        
        # Link to message
        self._link_to_message(node.node_id, message_id, entity.confidence)
        
        return node
    
    def upsert_intent_node(self, intent: Intent, message_id: UUID) -> Node:
        """Upsert an intent node and link to message"""
        node = self.db.query(Node).filter(
            Node.node_type == 'intent',
            Node.node_label == intent.primary_intent
        ).first()
        
        if node:
            node.frequency += 1
            node.last_updated = func.now()
        else:
            node = Node(
                node_type='intent',
                node_label=intent.primary_intent,
                properties={'confidence': intent.confidence}
            )
            self.db.add(node)
            self.db.flush()
        
        # Link to message
        self._link_to_message(node.node_id, message_id, intent.confidence)
        
        return node
    
    def upsert_emotion_node(self, emotion_name: str, score: float, message_id: UUID) -> Optional[Node]:
        """Upsert an emotion node and link to message"""
        if score <= 0.1:  # Skip low confidence emotions
            return None
        
        node = self.db.query(Node).filter(
            Node.node_type == 'emotion',
            Node.node_label == emotion_name
        ).first()
        
        if node:
            node.frequency += 1
            node.last_updated = func.now()
            
            # Update average score
            current_score = node.properties.get('average_score', score)
            node.properties['average_score'] = (current_score + score) / 2
        else:
            node = Node(
                node_type='emotion',
                node_label=emotion_name,
                properties={'average_score': score}
            )
            self.db.add(node)
            self.db.flush()
        
        # Link to message
        self._link_to_message(node.node_id, message_id, score)
        
        return node
    
    def _link_to_message(self, node_id: UUID, message_id: UUID, relevance: float):
        """Link node to message"""
        link = MessageNode(
            message_id=message_id,
            node_id=node_id,
            relevance_score=relevance
        )
        self.db.merge(link)  # merge will handle duplicates
    
    def get_node_by_id(self, node_id: UUID) -> Optional[Node]:
        """Get node by ID"""
        return self.db.query(Node).filter(Node.node_id == node_id).first()
    
    def get_nodes_by_type(self, node_type: str, limit: int = 100) -> List[Node]:
        """Get nodes by type"""
        return self.db.query(Node)\
            .filter(Node.node_type == node_type)\
            .order_by(Node.frequency.desc())\
            .limit(limit)\
            .all()