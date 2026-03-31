from typing import List, Dict
from models.message_models import NegationInfo

class NegationDetector:
    """Detects negation in text"""
    
    def __init__(self):
        self.negation_cues = ['not', 'no', 'never', 'none', "n't", 'cannot', 'without', 'lack']
    
    def process(self, doc) -> NegationInfo:
        """Detect negation and return information"""
        negated_tokens = []
        negation_phrases = []
        
        for token in doc:
            # Check if token is a negation cue
            if token.text.lower() in self.negation_cues:
                # Get the scope of negation (words in the subtree)
                scope = [child.text for child in token.subtree if child != token]
                negation_phrases.append({
                    'cue': token.text,
                    'position': token.i,
                    'scope': scope
                })
            
            # Check if token is negated (from custom attribute)
            if getattr(token._, 'negated', False):
                negated_tokens.append({
                    'token': token.text,
                    'position': token.i,
                    'lemma': token.lemma_
                })
        
        return NegationInfo(
            has_negation=len(negation_phrases) > 0,
            negation_count=len(negation_phrases),
            negation_phrases=negation_phrases,
            negated_tokens=negated_tokens
        )