"""Relevance scoring for context prioritization."""

from typing import List, Dict, Any
import math


class RelevanceScorer:
    """Scores context relevance for prioritization."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the relevance scorer.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
    
    def score_context(
        self,
        query: str,
        context_item: Dict[str, Any]
    ) -> float:
        """Score a context item's relevance to a query.
        
        Args:
            query: Query string.
            context_item: Context item.
            
        Returns:
            Relevance score (0-1).
        """
        content = context_item.get("content", "")
        metadata = context_item.get("metadata", {})
        
        query_terms = set(query.lower().split())
        content_terms = set(content.lower().split())
        
        if not query_terms:
            return 0.5
        
        overlap = len(query_terms & content_terms)
        jaccard = overlap / len(query_terms | content_terms)
        
        recency_score = self._score_recency(metadata)
        importance_score = metadata.get("importance", 0.5)
        
        combined_score = (jaccard * 0.5) + (recency_score * 0.3) + (importance_score * 0.2)
        
        return min(max(combined_score, 0.0), 1.0)
    
    def _score_recency(self, metadata: Dict[str, Any]) -> float:
        """Score recency based on timestamps.
        
        Args:
            metadata: Item metadata.
            
        Returns:
            Recency score (0-1).
        """
        import time
        
        created_at = metadata.get("created_at")
        if not created_at:
            return 0.5
        
        if isinstance(created_at, str):
            try:
                from datetime import datetime
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except:
                return 0.5
        
        try:
            age_hours = (time.time() - created_at.timestamp()) / 3600
            if age_hours < 1:
                return 1.0
            elif age_hours < 24:
                return 0.8
            elif age_hours < 168:
                return 0.6
            elif age_hours < 720:
                return 0.4
            else:
                return 0.2
        except:
            return 0.5
    
    def rank_contexts(
        self,
        query: str,
        contexts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank context items by relevance.
        
        Args:
            query: Query string.
            contexts: List of context items.
            
        Returns:
            Ranked context items with scores.
        """
        scored = []
        for ctx in contexts:
            score = self.score_context(query, ctx)
            ctx["relevance_score"] = score
            scored.append(ctx)
        
        scored.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return scored
    
    def filter_by_threshold(
        self,
        contexts: List[Dict[str, Any]],
        threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Filter contexts by relevance threshold.
        
        Args:
            contexts: List of context items.
            threshold: Minimum relevance score.
            
        Returns:
            Filtered context items.
        """
        return [ctx for ctx in contexts 
                if ctx.get("relevance_score", 0) >= threshold]
