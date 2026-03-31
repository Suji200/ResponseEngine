#!/usr/bin/env python3
"""
Detailed test to see ALL NLP component outputs in key-value pairs
"""

import os
import sys
import json
from pprint import pprint

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

print("="*70)
print("🔍 DETAILED NLP COMPONENT TEST")
print("="*70)

# Import all components
try:
    from Nlp.tokenizer import Tokenizer
    from Nlp.entity_extractor import EntityExtractor
    from Nlp.sentiment_analyzer import SentimentAnalyzer
    from Nlp.emotion_detector import EmotionDetector
    from Nlp.intent_classifier import IntentClassifier
    from Nlp.negation_detector import NegationDetector
    from Nlp.dependency_parser import DependencyParser
    from models.message_models import Sentiment, Emotion, Intent, Token, Entity, NegationInfo, DependencyRelation
    
    print("✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Load spaCy
import spacy
print("\n🔄 Loading spaCy model...")
try:
    nlp = spacy.load("en_core_web_lg")
    print("✅ spaCy model loaded")
except:
    print("⚠️  Downloading spaCy model...")
    spacy.cli.download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")

# Initialize components
tokenizer = Tokenizer(nlp)
entity_extractor = EntityExtractor(nlp)
sentiment_analyzer = SentimentAnalyzer()
emotion_detector = EmotionDetector()
intent_classifier = IntentClassifier()
negation_detector = NegationDetector()
dependency_parser = DependencyParser()

# Test message
test_message = "I really hate this product! It doesn't work at all. Can you help me fix it?"
print(f"\n📨 Test Message: \"{test_message}\"")

# Process with spaCy
doc = nlp(test_message)

print("\n" + "="*70)
print("📊 COMPONENT OUTPUTS (Key-Value Pairs)")
print("="*70)

# 1. TOKENIZER - Show all tokens with their attributes
print("\n1️⃣ TOKENIZER OUTPUT:")
print("-"*50)
tokens = tokenizer.process(doc)
print(f"Total tokens: {len(tokens)}")
print("\nToken Details (first 5):")
for i, token in enumerate(tokens[:5]):
    print(f"\n   Token {i+1}:")
    print(f"     text: '{token.text}'")
    print(f"     lemma: '{token.lemma}'")
    print(f"     pos: '{token.pos}'")
    print(f"     tag: '{token.tag}'")
    print(f"     dep: '{token.dep}'")
    print(f"     is_stop: {token.is_stop}")
    print(f"     negated: {token.negated}")

# 2. ENTITY EXTRACTOR
print("\n" + "="*70)
print("2️⃣ ENTITY EXTRACTOR OUTPUT:")
print("-"*50)
entities = entity_extractor.process(doc)
print(f"Total entities: {len(entities)}")
for i, entity in enumerate(entities):
    print(f"\n   Entity {i+1}:")
    print(f"     text: '{entity.text}'")
    print(f"     label: '{entity.label}'")
    print(f"     confidence: {entity.confidence}")
    print(f"     description: '{entity.description}'")

# 3. SENTIMENT ANALYZER
print("\n" + "="*70)
print("3️⃣ SENTIMENT ANALYZER OUTPUT:")
print("-"*50)
sentiment = sentiment_analyzer.process(test_message)
print("\n   Sentiment Object Attributes:")
print(f"     class: '{sentiment.sentiment_class}'")
print(f"     polarity: {sentiment.polarity:.3f}")
print(f"     subjectivity: {sentiment.subjectivity:.3f}")
print(f"     positive_score: {sentiment.positive_score:.3f}")
print(f"     negative_score: {sentiment.negative_score:.3f}")
print(f"     neutral_score: {sentiment.neutral_score:.3f}")
print("\n   As Dictionary:")
pprint(sentiment.to_dict())

# 4. EMOTION DETECTOR
print("\n" + "="*70)
print("4️⃣ EMOTION DETECTOR OUTPUT:")
print("-"*50)
emotions = emotion_detector.process(doc)
print("\n   Raw Emotion Object:")
print(f"     {emotions}")
print("\n   As Dictionary:")
emotion_dict = emotions.to_dict()
if emotion_dict:
    for emotion, score in emotion_dict.items():
        print(f"     {emotion}: {score:.3f}")
else:
    print("     No emotions detected")

# 5. INTENT CLASSIFIER
print("\n" + "="*70)
print("5️⃣ INTENT CLASSIFIER OUTPUT:")
print("-"*50)
intent = intent_classifier.process(doc)
print("\n   Intent Object Attributes:")
print(f"     primary_intent: '{intent.primary_intent}'")
print(f"     confidence: {intent.confidence:.3f}")
print(f"     all_intents: {intent.all_intents}")
print("\n   As Dictionary:")
pprint(intent.to_dict())

# 6. NEGATION DETECTOR
print("\n" + "="*70)
print("6️⃣ NEGATION DETECTOR OUTPUT:")
print("-"*50)
negation = negation_detector.process(doc)
print("\n   Negation Object Attributes:")
print(f"     has_negation: {negation.has_negation}")
print(f"     negation_count: {negation.negation_count}")
if negation.negation_phrases:
    print(f"     negation_phrases: {negation.negation_phrases}")
if negation.negated_tokens:
    print(f"     negated_tokens: {negation.negated_tokens}")
print("\n   As Dictionary:")
pprint(negation.to_dict())

# 7. DEPENDENCY PARSER
print("\n" + "="*70)
print("7️⃣ DEPENDENCY PARSER OUTPUT:")
print("-"*50)
deps = dependency_parser.process(doc)
print(f"Total dependencies: {len(deps)}")
print("\nFirst 5 Dependency Relations:")
for i, dep in enumerate(deps[:5]):
    print(f"\n   Relation {i+1}:")
    print(f"     token: '{dep.token}'")
    print(f"     head: '{dep.head}'")
    print(f"     dep: '{dep.dep}'")
    print(f"     children: {dep.children[:3]}")

print("\n" + "="*70)
print("✅ TEST COMPLETE - All components executed!")
print("="*70)

# Bonus: Complete Processed Message (like your pipeline would produce)
print("\n" + "="*70)
print("📦 COMPLETE PROCESSED MESSAGE (All components combined)")
print("="*70)

complete_result = {
    'raw_text': test_message,
    'tokens': [t.to_dict() for t in tokens],
    'entities': [e.to_dict() for e in entities],
    'sentiment': sentiment.to_dict(),
    'emotions': emotions.to_dict(),
    'intent': intent.to_dict(),
    'negation': negation.to_dict(),
    'dependency_parse': [d.to_dict() for d in deps]
}

print("\nJSON Summary (first 500 chars):")
print(json.dumps(complete_result, indent=2)[:500] + "...")