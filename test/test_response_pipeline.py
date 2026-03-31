import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from response_generation import ResponsePipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_pipeline():
    # Initialize the pipeline
    pipeline = ResponsePipeline()
    
    # Mock data for demonstration
    
    # 1. New user scenario
    print("-" * 50)
    print("SCENARIO 1: New User Greeting")
    state = {'user_properties': {'is_new_user': True}}
    trigger_score = {'total_score': 10, 'action_level': 'low'}
    context_data = {'user_name': 'Alice'}
    
    result = pipeline.run(state, trigger_score, context_data)
    print(f"Intent: {result['intent']}")
    print(f"Delay: {result['delay_applied']}s")
    
    # 2. Critical anger scenario
    print("-" * 50)
    print("SCENARIO 2: De-escalation (Critical)")
    state = {'user_properties': {'is_new_user': False}}
    trigger_score = {
        'total_score': 95, 
        'action_level': 'critical', 
        'triggered_rules': [{'rule_name': 'anger_detected'}]
    }
    context_data = {'user_name': 'Bob'}
    
    result = pipeline.run(state, trigger_score, context_data)
    print(f"Intent: {result['intent']}")
    print(f"Delay: {result['delay_applied']}s")

    # 3. Subscription renewal scenario
    print("-" * 50)
    print("SCENARIO 3: Renewal Reminder")
    state = {'user_properties': {'subscription_status': 'expired'}}
    trigger_score = {'total_score': 30, 'action_level': 'medium'}
    context_data = {'user_name': 'Charlie'}
    
    result = pipeline.run(state, trigger_score, context_data)
    print(f"Intent: {result['intent']}")
    print(f"Delay: {result['delay_applied']}s")

if __name__ == "__main__":
    test_pipeline()
