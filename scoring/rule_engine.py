from typing import Dict, Any, List, Optional
from .rules import RuleSet, Rule, RulePriority
from .thresholds import ThresholdManager
import logging
from datetime import datetime

class RuleEngine:
    """Engine for evaluating rules and calculating scores"""
    
    def __init__(self, ruleset: RuleSet, threshold_manager: ThresholdManager):
        self.ruleset = ruleset
        self.threshold_manager = threshold_manager
        self.logger = logging.getLogger(__name__)
        self.evaluation_history: List[Dict[str, Any]] = []
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate all rules against the given context
        
        Args:
            context: Dictionary containing state information (user_id, session_id, 
                    message_count, avg_sentiment, etc.)
        
        Returns:
            Dictionary with evaluation results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_score': 0,
            'triggered_rules': [],
            'thresholds_exceeded': [],
            'categories': {},
            'recommendations': []
        }
        
        category_scores = {}
        
        # Evaluate each rule
        for rule in self.ruleset.rules:
            try:
                evaluation = rule.evaluate(context)
                
                if evaluation['triggered']:
                    results['triggered_rules'].append(evaluation)
                    results['total_score'] += evaluation['weighted_score']
                    
                    # Track category scores
                    category = self._get_rule_category(rule)
                    if category not in category_scores:
                        category_scores[category] = 0
                    category_scores[category] += evaluation['weighted_score']
                    
                    # Check thresholds
                    if evaluation['threshold_exceeded']:
                        results['thresholds_exceeded'].append({
                            'rule_name': rule.name,
                            'score': evaluation['weighted_score'],
                            'threshold': rule.threshold,
                            'priority': evaluation['priority']
                        })
                        
                        # Generate recommendations
                        recommendation = self._generate_recommendation(rule, evaluation)
                        if recommendation:
                            results['recommendations'].append(recommendation)
                            
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.name}: {e}")
        
        results['categories'] = category_scores
        
        # Determine overall action level
        results['action_level'] = self.threshold_manager.determine_action_level(
            results['total_score'],
            results['thresholds_exceeded']
        )
        
        # Store in history
        self.evaluation_history.append({
            'timestamp': results['timestamp'],
            'total_score': results['total_score'],
            'action_level': results['action_level']
        })
        
        # Trim history if needed
        if len(self.evaluation_history) > 100:
            self.evaluation_history = self.evaluation_history[-100:]
        
        return results
    
    def _get_rule_category(self, rule: Rule) -> str:
        """Get the category of a rule"""
        for category, rules in self.ruleset.categories.items():
            if rule in rules:
                return category
        return 'default'
    
    def _generate_recommendation(self, rule: Rule, evaluation: Dict) -> Optional[str]:
        """Generate recommendation based on rule evaluation"""
        recommendations = {
            'negative_sentiment_escalation': 'Consider immediate customer support intervention',
            'frequent_complaints': 'Escalate to supervisor for review',
            'urgent_help_request': 'Prioritize this user in support queue',
            'entity_frequency_alert': 'Monitor user for potential issue patterns',
            'anger_detected': 'De-escalation techniques recommended',
            'multiple_questions': 'Provide comprehensive FAQ response'
        }
        
        return recommendations.get(rule.name)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        if not self.evaluation_history:
            return {}
        
        scores = [h['total_score'] for h in self.evaluation_history]
        
        return {
            'average_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'evaluations_count': len(self.evaluation_history),
            'recent_action_level': self.evaluation_history[-1]['action_level'] if self.evaluation_history else None
        }