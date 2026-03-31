import spacy
from typing import List
from models.message_models import Token

class Tokenizer:
    """Handles tokenization and basic token features"""
    
    def __init__(self, nlp):
        self.nlp = nlp
    
    def process(self, doc) -> List[Token]:
        """Extract tokens with their features"""
        tokens = []
        for token in doc:
            tokens.append(Token(
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                tag=token.tag_,
                dep=token.dep_,
                shape=token.shape_,
                is_alpha=token.is_alpha,
                is_stop=token.is_stop,
                negated=getattr(token._, 'negated', False),
                entity_type=token.ent_type_ if token.ent_type_ else None
            ))
        return tokens