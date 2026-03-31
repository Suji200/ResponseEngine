from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from ...models.database_models import Message, MessageNode
from ...models.message_models import ProcessedMessage
import json

class MessageRepository:
    """Handles message database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, processed: ProcessedMessage) -> Message:
        """Create a new message record"""
        message = Message(
            session_id=processed.session_id,
            user_id=processed.user_id,
            raw_text=processed.raw_text,
            tokens=[t.to_dict() for t in processed.tokens],
            entities=[e.to_dict() for e in processed.entities],
            sentiment=processed.sentiment.to_dict(),
            emotions=processed.emotions.to_dict(),
            intent=processed.intent.to_dict(),
            negation=processed.negation.to_dict(),
            dependency_parse=[d.to_dict() for d in processed.dependency_parse],
            metadata=processed.metadata
        )
        
        self.db.add(message)
        self.db.flush()  # Get the ID without committing
        return message
    
    def get_by_id(self, message_id: UUID) -> Optional[Message]:
        """Get message by ID"""
        return self.db.query(Message).filter(Message.message_id == message_id).first()
    
    def get_by_session(self, session_id: str, limit: int = 10) -> List[Message]:
        """Get messages by session ID"""
        return self.db.query(Message)\
            .filter(Message.session_id == session_id)\
            .order_by(Message.processed_at.desc())\
            .limit(limit)\
            .all()
    
    def get_by_user(self, user_id: str, limit: int = 10) -> List[Message]:
        """Get messages by user ID"""
        return self.db.query(Message)\
            .filter(Message.user_id == user_id)\
            .order_by(Message.processed_at.desc())\
            .limit(limit)\
            .all()
    
    def get_graph_state(self, session_id: Optional[str], user_id: Optional[str]) -> Dict[str, Any]:
        """Get aggregated graph state for scoring"""
        from sqlalchemy import func, text
        
        # Get recent messages
        query = self.db.query(Message)
        if session_id:
            query = query.filter(Message.session_id == session_id)
        if user_id:
            query = query.filter(Message.user_id == user_id)
        
        recent_messages = query.order_by(Message.processed_at.desc()).limit(10).all()
        
        if not recent_messages:
            return {
                'message_count': 0,
                'avg_sentiment': 0,
                'entity_types': [],
                'dominant_intent': None
            }
        
        # Calculate average sentiment
        sentiments = [m.sentiment.get('polarity', 0) for m in recent_messages if m.sentiment]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Get entity types
        entity_types = []
        for msg in recent_messages:
            if msg.entities:
                for entity in msg.entities:
                    if isinstance(entity, dict) and 'label' in entity:
                        entity_types.append(entity['label'])
        
        # Get dominant intent
        intents = [m.intent.get('primary_intent') for m in recent_messages if m.intent and m.intent.get('primary_intent')]
        dominant_intent = max(set(intents), key=intents.count) if intents else None
        
        return {
            'message_count': len(recent_messages),
            'avg_sentiment': avg_sentiment,
            'entity_types': list(set(entity_types)),
            'dominant_intent': dominant_intent
        }