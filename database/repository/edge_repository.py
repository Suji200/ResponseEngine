from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from uuid import UUID
from ...models.database_models import Edge

class EdgeRepository:
    """Handles edge database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_update(self, 
                        source_id: UUID, 
                        target_id: UUID, 
                        edge_type: str,
                        properties: Optional[dict] = None) -> Edge:
        """Create or update an edge"""
        
        edge = self.db.query(Edge).filter(
            Edge.source_node_id == source_id,
            Edge.target_node_id == target_id,
            Edge.edge_type == edge_type
        ).first()
        
        if edge:
            # Update existing edge
            edge.weight += 1
            edge.last_updated = func.now()
            if properties:
                # Merge properties
                current_props = edge.properties or {}
                current_props.update(properties)
                edge.properties = current_props
        else:
            # Create new edge
            edge = Edge(
                source_node_id=source_id,
                target_node_id=target_id,
                edge_type=edge_type,
                properties=properties or {}
            )
            self.db.add(edge)
            self.db.flush()
        
        return edge
    
    def get_edges_from_node(self, node_id: UUID, edge_type: Optional[str] = None) -> List[Edge]:
        """Get all edges from a node"""
        query = self.db.query(Edge).filter(Edge.source_node_id == node_id)
        if edge_type:
            query = query.filter(Edge.edge_type == edge_type)
        return query.all()
    
    def get_edges_to_node(self, node_id: UUID, edge_type: Optional[str] = None) -> List[Edge]:
        """Get all edges to a node"""
        query = self.db.query(Edge).filter(Edge.target_node_id == node_id)
        if edge_type:
            query = query.filter(Edge.edge_type == edge_type)
        return query.all()