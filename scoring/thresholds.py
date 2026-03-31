from typing import Dict, Any, List, Optional
from enum import Enum

class ActionLevel(Enum):
    NONE = 'no_action'
    LOW = 'monitor'
    MEDIUM = 'notify'
    HIGH = 'escalate'
    CRITICAL = 'immediate_intervention'

class ThresholdManager:
    """Manages thresholds for scoring and actions"""
    
    def __init__(self, config: Optional[Dict[str, float]] = None):
        self.thresholds = {
            'low': config.get('low', 5.0) if config else 5.0,
            'medium': config.get('medium', 10.0) if config else 10.0,
            'high': config.get('high', 20.0) if config else 20.0,
            'critical': config.get('critical', 30.0) if config else 30.0
        }
        
        self.category_thresholds = {
            'sentiment': 0.7,
            'intent': 0.8,
            'entities': 0.5,
            'behavior': 0.6
        }
    
    def determine_action_level(self, total_score: float, exceeded_thresholds: List[Dict]) -> ActionLevel:
        """
        Determine action level based on score and exceeded thresholds
        
        Args:
            total_score: Total weighted score
            exceeded_thresholds: List of thresholds exceeded
        
        Returns:
            Appropriate ActionLevel
        """
        # Check critical thresholds first
        if total_score >= self.thresholds['critical']:
            return ActionLevel.CRITICAL
        
        # Check if any high priority thresholds were exceeded
        high_priority_exceeded = any(
            t.get('priority', 0) >= 3 for t in exceeded_thresholds
        )
        
        if high_priority_exceeded or total_score >= self.thresholds['high']:
            return ActionLevel.HIGH
        
        if total_score >= self.thresholds['medium']:
            return ActionLevel.MEDIUM
        
        if total_score >= self.thresholds['low']:
            return ActionLevel.LOW
        
        return ActionLevel.NONE
    
    def is_category_alert(self, category: str, score: float) -> bool:
        """Check if category score exceeds its threshold"""
        threshold = self.category_thresholds.get(category, 0.5)
        return score >= threshold
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get all thresholds"""
        return {
            'score_thresholds': self.thresholds,
            'category_thresholds': self.category_thresholds
        }
    
    def update_threshold(self, threshold_type: str, value: float):
        """Update a specific threshold"""
        if threshold_type in self.thresholds:
            self.thresholds[threshold_type] = value
        elif threshold_type in self.category_thresholds:
            self.category_thresholds[threshold_type] = value