from typing import Dict
from collections import defaultdict
from models.message_models import Intent

class IntentClassifier:
    """Classifies user intent from text"""
    
    def __init__(self):
        self.intent_patterns = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'farewell': ['bye', 'goodbye', 'see you', 'take care', 'farewell'],
            'question': ['?', 'what', 'when', 'where', 'who', 'why', 'how', 'can you', 'could you'],
            'request': ['please', 'can you', 'could you', 'would you', 'i need', 'i want'],
            'complaint': ['problem', 'issue', 'not working', 'broken', 'bad', 'terrible', 'awful'],
            'feedback': ['suggestion', 'idea', 'think', 'opinion', 'recommend', 'suggest'],
            'help': ['help', 'support', 'assist', 'trouble', 'difficulty'],
            'information': ['tell me about', 'what is', 'define', 'explain', 'meaning of'],
            'appreciation': ['thank', 'thanks', 'appreciate', 'grateful', 'good job'],
            'confirmation': ['yes', 'yeah', 'correct', 'right', 'agree', 'confirm'],
            'negation': ['no', 'not', "don't", "doesn't", 'never', 'none']
        }
    
    def process(self, doc) -> Intent:
        """Detect intent from document"""
        text_lower = doc.text.lower()
        intents = defaultdict(float)
        
        # Check for intent patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    intents[intent] += 1.0
                elif '?' in text_lower and intent == 'question':
                    intents[intent] = max(intents[intent], 0.8)
        
        # Check for imperative sentences (commands)
        for token in doc:
            if token.dep_ == 'ROOT' and token.tag_ == 'VB' and token.text.lower() not in ['please']:
                intents['command'] = max(intents.get('command', 0), 0.6)
        
        # Normalize intent scores
        total = sum(intents.values())
        if total > 0:
            for intent in intents:
                intents[intent] /= total
        
        # Get primary intent
        primary_intent = max(intents.items(), key=lambda x: x[1]) if intents else ('unknown', 0.0)
        
        return Intent(
            primary_intent=primary_intent[0],
            confidence=primary_intent[1],
            all_intents=dict(intents)
        )