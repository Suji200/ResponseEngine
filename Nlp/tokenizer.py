
from dataclasses import dataclass
from typing import List

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
    entity_type: str = None
    
    def to_dict(self):
        return {
            'text': self.text,
            'lemma': self.lemma,
            'pos': self.pos,
            'tag': self.tag,
            'dep': self.dep,
            'shape': self.shape,
            'is_alpha': self.is_alpha,
            'is_stop': self.is_stop,
            'negated': self.negated,
            'entity_type': self.entity_type
        }

class Tokenizer:
    def __init__(self, nlp):
        self.nlp = nlp
    
    def process(self, doc) -> List[Token]:
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