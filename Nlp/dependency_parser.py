from typing import List
from models.message_models import DependencyRelation

class DependencyParser:
    """Extracts dependency parse information"""
    
    def process(self, doc) -> List[DependencyRelation]:
        """Extract dependency relations"""
        dependencies = []
        for token in doc:
            dependencies.append(DependencyRelation(
                token=token.text,
                head=token.head.text,
                dep=token.dep_,
                children=[child.text for child in token.children],
                pos=token.pos_
            ))
        return dependencies