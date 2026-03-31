from typing import Dict
from collections import defaultdict
from models.message_models import Emotion

class EmotionDetector:
    """Detects emotions in text using keyword matching"""
    
    def __init__(self):
        self.emotion_keywords = {
            'joy': ['happy', 'glad', 'excited', 'delighted', 'pleased', 'joy', 'wonderful'],
            'sadness': ['sad', 'unhappy', 'depressed', 'gloomy', 'miserable', 'heartbroken', 'down', 'empty', 'lonely'],
            'anger': ['angry', 'furious', 'outraged', 'mad', 'annoyed', 'frustrated'],
            'fear': ['afraid', 'scared', 'terrified', 'worried', 'anxious', 'nervous'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned'],
            'love': ['love', 'adore', 'cherish', 'treasure', 'worship'],
            'venting': ['vent', 'rant', 'unburden', 'pour out', 'get it out']
        }
    
    def process(self, doc) -> Emotion:
        """Detect emotions from document"""
        emotion_scores = defaultdict(float)
        
        for token in doc:
            token_lower = token.text.lower()
            token_lemma = token.lemma_.lower()
            
            for emotion, keywords in self.emotion_keywords.items():
                if token_lower in keywords or token_lemma in keywords:
                    emotion_scores[emotion] += 1.0
        
        # Normalize scores
        total = sum(emotion_scores.values())
        if total > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] /= total
        
        return Emotion(
            joy=emotion_scores.get('joy', 0),
            sadness=emotion_scores.get('sadness', 0),
            anger=emotion_scores.get('anger', 0),
            fear=emotion_scores.get('fear', 0),
            surprise=emotion_scores.get('surprise', 0),
            love=emotion_scores.get('love', 0),
            venting=emotion_scores.get('venting', 0)
        )
