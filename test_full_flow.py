import os
import sys
import json
import logging
from pprint import pprint

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Import NLP components
from Nlp.tokenizer import Tokenizer
from Nlp.entity_extractor import EntityExtractor
from Nlp.sentiment_analyzer import SentimentAnalyzer
from Nlp.emotion_detector import EmotionDetector
from Nlp.intent_classifier import IntentClassifier
from Nlp.negatiton_detector import NegationDetector
from Nlp.dependency_parser import DependencyParser

# Import Scoring components
from scoring.rules import RuleSet, Rule, RulePriority
from scoring.thresholds import ThresholdManager
from scoring.rule_engine import RuleEngine

# Import Response Generation components
from response_generation import ResponsePipeline

import spacy

def run_full_flow(text, user_name="User"):
    print("\n" + "="*80)
    print(f"🚀 FULL FLOW TEST: \"{text}\"")
    print("="*80)

    # 1. NLP EXTRACTION
    print("\nStep 1: Extracting NLP features...")
    try:
        nlp = spacy.load("en_core_web_lg")
    except:
        print("Downloading spaCy model...")
        spacy.cli.download("en_core_web_lg")
        nlp = spacy.load("en_core_web_lg")

    doc = nlp(text)
    
    tokenizer = Tokenizer(nlp)
    entity_extractor = EntityExtractor(nlp)
    sentiment_analyzer = SentimentAnalyzer()
    emotion_detector = EmotionDetector()
    intent_classifier = IntentClassifier()
    negation_detector = NegationDetector()
    
    tokens = tokenizer.process(doc)
    entities = entity_extractor.process(doc)
    sentiment = sentiment_analyzer.process(text)
    emotions = emotion_detector.process(doc)
    intent = intent_classifier.process(doc)
    negation = negation_detector.process(doc)

    sentiment_dict = sentiment.to_dict()
    emotion_dict = emotions.to_dict()

    print(f"   Sentiment: {sentiment.sentiment_class} (Polarity: {sentiment.polarity:.2f})")
    print(f"   Emotions: {emotion_dict}")
    print(f"   Primary Intent: {intent.primary_intent}")

    # 2. SCORING / RULE ENGINE
    print("\nStep 2: Calculating Trigger Scores...")
    
    # Define rules using the actual Rule class structure
    negative_sentiment_rule = Rule(
        name="negative_sentiment_escalation",
        description="Triggered when sentiment polarity is negative",
        weight=50,
        priority=RulePriority.HIGH,
        condition=lambda ctx: ctx.get('sentiment', {}).get('polarity', 0) < -0.1,
        score_calculator=lambda ctx: abs(ctx.get('sentiment', {}).get('polarity', 0)),
        threshold=10
    )

    sadness_rule = Rule(
        name="sadness_detected",
        description="Triggered when sadness emotion is high",
        weight=40,
        priority=RulePriority.MEDIUM,
        condition=lambda ctx: ctx.get('emotions', {}).get('sadness', 0) > 0.3,
        score_calculator=lambda ctx: ctx.get('emotions', {}).get('sadness', 0),
        threshold=5
    )

    venting_rule = Rule(
        name="venting_detected",
        description="Triggered when user intent is to vent",
        weight=60,
        priority=RulePriority.HIGH,
        condition=lambda ctx: ctx.get('emotions', {}).get('venting', 0) > 0,
        score_calculator=lambda ctx: ctx.get('emotions', {}).get('venting', 0) * 10,
        threshold=5
    )
    
    ruleset = RuleSet(name="Default Rules")
    ruleset.add_rule(negative_sentiment_rule)
    ruleset.add_rule(sadness_rule)
    ruleset.add_rule(venting_rule)
    
    threshold_manager = ThresholdManager()
    rule_engine = RuleEngine(ruleset, threshold_manager)
    
    context = {
        "sentiment": sentiment_dict,
        "emotions": emotion_dict,
        "intent": intent.to_dict()
    }
    
    trigger_score = rule_engine.evaluate(context)
    print(f"   Total Score: {trigger_score['total_score']}")
    print(f"   Action Level: {trigger_score['action_level']}")
    print(f"   Triggered Rules: {[r['rule_name'] for r in trigger_score['triggered_rules']]}")

    # 3. RESPONSE GENERATION
    print("\nStep 3: Generating Response...")
    
    state = {
        'user_properties': {
            'user_name': user_name,
            'is_new_user': False,
            'subscription_status': 'active'
        }
    }
    
    context_data = {
        'user_name': user_name,
        'detected_emotion': max(emotion_dict.items(), key=lambda x: x[1])[0] if emotion_dict else "neutral"
    }
    
    custom_templates = {
        "empathetic_support": [
            "I'm really sorry to hear you're feeling this way, {{ user_name }}. It's completely okay to vent. Sometimes feeling empty is part of the process, but I'm here to listen.",
            "I hear you, {{ user_name }}. It sounds like you're going through a tough time even if you can't put your finger on why. I'm here for you."
        ],
        "emergency_escalate": [
            "I can tell you're going through a really hard time, {{ user_name }}. I'm here to listen, and I've also flagged this for our support team to make sure you get the attention you need.",
            "It sounds like things are very heavy right now. I'm here with you."
        ],
        "de_escalate": [
            "I understand you're feeling down, {{ user_name }}. Please know that I'm here to support you in any way I can."
        ],
        "standard_support": [
            "I'm here to help, {{ user_name }}. Tell me more about how you're feeling.",
            "I'm listening. Please feel free to share more."
        ],
        "general_greeting": [
            "Hello {{ user_name }}, I'm here. What's on your mind?"
        ]
    }
    
    pipeline = ResponsePipeline(templates=custom_templates)
    response_result = pipeline.run(state, trigger_score, context_data)
    
    print("\n" + "="*80)
    print("✅ FINAL PIPELINE OUTPUT")
    print("="*80)
    print(f"Final Intent: {response_result['intent']}")
    print(f"Template Used: {response_result['template_used']}")
    print(f"Dispatch Delay: {response_result['delay_applied']}s")
    print(f"Response Content: {response_result['content']}")

if __name__ == "__main__":
    text = "okay i need to vent. i've been feeling super down lately and i don't even know why. like nothing is technically wrong but i just feel empty"
    run_full_flow(text)
