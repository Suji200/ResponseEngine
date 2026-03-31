from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'
    
    node_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_type = Column(String(50), nullable=False)
    node_label = Column(String(255), nullable=False)
    properties = Column(JSON, default={})
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confidence_score = Column(Float, default=1.0)
    frequency = Column(Integer, default=1)
    
    # Relationships
    source_edges = relationship("Edge", foreign_keys="Edge.source_node_id", back_populates="source")
    target_edges = relationship("Edge", foreign_keys="Edge.target_node_id", back_populates="target")
    message_links = relationship("MessageNode", back_populates="node")
    
    __table_args__ = (
        UniqueConstraint('node_type', 'node_label', name='unique_node_type_label'),
    )

class Edge(Base):
    __tablename__ = 'edges'
    
    edge_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_node_id = Column(UUID(as_uuid=True), ForeignKey('nodes.node_id', ondelete='CASCADE'))
    target_node_id = Column(UUID(as_uuid=True), ForeignKey('nodes.node_id', ondelete='CASCADE'))
    edge_type = Column(String(50), nullable=False)
    properties = Column(JSON, default={})
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    weight = Column(Float, default=1.0)
    
    # Relationships
    source = relationship("Node", foreign_keys=[source_node_id], back_populates="source_edges")
    target = relationship("Node", foreign_keys=[target_node_id], back_populates="target_edges")
    
    __table_args__ = (
        UniqueConstraint('source_node_id', 'target_node_id', 'edge_type', name='unique_edge'),
    )

class Message(Base):
    __tablename__ = 'messages'
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255))
    user_id = Column(String(255))
    raw_text = Column(String, nullable=False)
    tokens = Column(JSON)
    entities = Column(JSON)
    sentiment = Column(JSON)
    emotions = Column(JSON)
    intent = Column(JSON)
    negation = Column(JSON)
    dependency_parse = Column(JSON)
    processed_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    # Relationships
    node_links = relationship("MessageNode", back_populates="message")

class MessageNode(Base):
    __tablename__ = 'message_nodes'
    
    message_id = Column(UUID(as_uuid=True), ForeignKey('messages.message_id', ondelete='CASCADE'), primary_key=True)
    node_id = Column(UUID(as_uuid=True), ForeignKey('nodes.node_id', ondelete='CASCADE'), primary_key=True)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="node_links")
    node = relationship("Node", back_populates="message_links")