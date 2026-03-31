
from textblob import TextBlob
from typing import Dict
from models.message_models import Sentiment

class SentimentAnalyzer:
    """Analyzes sentiment of text"""
    
    def process(self, text: str) -> Sentiment:
        """Analyze sentiment and return scores"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment_class = 'positive'
        elif polarity < -0.1:
            sentiment_class = 'negative'
        else:
            sentiment_class = 'neutral'
        
        return Sentiment(
            polarity=polarity,
            subjectivity=subjectivity,
            sentiment_class=sentiment_class,
            positive_score=max(0, polarity),
            negative_score=max(0, -polarity),
            neutral_score=1 - abs(polarity)
        )