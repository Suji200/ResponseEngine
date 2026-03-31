
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class Token:
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    shape: str
    is_alpha: bool
    is_stop: bool
    negated: bool = False
    entity_type: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Entity:
    text: str
    label: str
    start_char: int
    end_char: int
    confidence: float = 1.0
    description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Sentiment:
    polarity: float
    subjectivity: float
    sentiment_class: str
    positive_score: float
    negative_score: float
    neutral_score: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Emotion:
    joy: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    surprise: float = 0.0
    love: float = 0.0
    venting: float = 0.0
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v > 0}

@dataclass
class Intent:
    primary_intent: str
    confidence: float
    all_intents: Dict[str, float]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class NegationInfo:
    has_negation: bool
    negation_count: int
    negation_phrases: List[Dict]
    negated_tokens: List[Dict]
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class DependencyRelation:
    token: str
    head: str
    dep: str
    children: List[str]
    pos: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class ProcessedMessage:
    raw_text: str
    tokens: List[Token]
    entities: List[Entity]
    sentiment: Sentiment
    emotions: Emotion
    intent: Intent
    negation: NegationInfo
    dependency_parse: List[DependencyRelation]
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'raw_text': self.raw_text,
            'tokens': [t.to_dict() for t in self.tokens],
            'entities': [e.to_dict() for e in self.entities],
            'sentiment': self.sentiment.to_dict(),
            'emotions': self.emotions.to_dict(),
            'intent': self.intent.to_dict(),
            'negation': self.negation.to_dict(),
            'dependency_parse': [d.to_dict() for d in self.dependency_parse],
            'session_id': self.session_id,
            'user_id': self.user_id,
            'metadata': self.metadata,
            'processed_at': self.processed_at.isoformat()
        }