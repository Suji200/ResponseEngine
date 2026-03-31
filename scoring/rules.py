from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass
from enum import Enum

class RulePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Rule:
    """Represents a scoring rule"""
    name: str
    description: str
    weight: float
    priority: RulePriority
    condition: Callable[[Dict[str, Any]], bool]
    score_calculator: Callable[[Dict[str, Any]], float]
    threshold: float
    metadata: Dict[str, Any] = None
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the rule against the given context"""
        if not self.condition(context):
            return {
                'triggered': False,
                'rule_name': self.name,
                'score': 0,
                'weight': self.weight
            }
        
        raw_score = self.score_calculator(context)
        weighted_score = raw_score * self.weight
        
        return {
            'triggered': True,
            'rule_name': self.name,
            'raw_score': raw_score,
            'weighted_score': weighted_score,
            'weight': self.weight,
            'threshold': self.threshold,
            'threshold_exceeded': weighted_score >= self.threshold,
            'priority': self.priority.value
        }

class RuleSet:
    """Collection of rules with management capabilities"""
    
    def __init__(self, name: str):
        self.name = name
        self.rules: List[Rule] = []
        self.categories: Dict[str, List[Rule]] = {}
    
    def add_rule(self, rule: Rule, category: str = 'default'):
        """Add a rule to the ruleset"""
        self.rules.append(rule)
        
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(rule)
    
    def remove_rule(self, rule_name: str):
        """Remove a rule by name"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        for category in self.categories:
            self.categories[category] = [r for r in self.categories[category] if r.name != rule_name]
    
    def get_rules_by_priority(self, priority: RulePriority) -> List[Rule]:
        """Get all rules with specific priority"""
        return [r for r in self.rules if r.priority == priority]
    
    def get_rules_by_category(self, category: str) -> List[Rule]:
        """Get all rules in a category"""
        return self.categories.get(category, [])