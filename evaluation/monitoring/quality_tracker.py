"""Quality tracking for monitoring."""

from typing import Dict, Any, List
from datetime import datetime


class QualityTracker:
    """Tracks response quality metrics."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the tracker.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
        self._ratings = []
        self._feedback = []
    
    def record_rating(
        self,
        rating: int,
        context: Dict[str, Any] = None
    ) -> None:
        """Record a quality rating.
        
        Args:
            rating: Rating score (1-5).
            context: Additional context.
        """
        self._ratings.append({
            "timestamp": datetime.utcnow().isoformat(),
            "rating": rating,
            "context": context or {}
        })
    
    def record_feedback(
        self,
        feedback_type: str,
        comment: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Record user feedback.
        
        Args:
            feedback_type: Type of feedback.
            comment: Feedback comment.
            context: Additional context.
        """
        self._feedback.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": feedback_type,
            "comment": comment,
            "context": context or {}
        })
    
    def get_average_rating(self) -> float:
        """Get average rating.
        
        Returns:
            Average rating (1-5).
        """
        if not self._ratings:
            return 0.0
        
        return sum(r["rating"] for r in self._ratings) / len(self._ratings)
    
    def get_rating_distribution(self) -> Dict[str, int]:
        """Get rating distribution.
        
        Returns:
            Rating distribution.
        """
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in self._ratings:
            score = rating["rating"]
            if score in distribution:
                distribution[score] += 1
        return distribution
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent feedback.
        
        Args:
            limit: Maximum number of feedback items.
            
        Returns:
            Recent feedback items.
        """
        return self._feedback[-limit:]
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get quality summary.
        
        Returns:
            Quality summary.
        """
        return {
            "total_ratings": len(self._ratings),
            "average_rating": self.get_average_rating(),
            "rating_distribution": self.get_rating_distribution(),
            "total_feedback": len(self._feedback),
            "recent_feedback": self.get_recent_feedback(5)
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._ratings.clear()
        self._feedback.clear()
