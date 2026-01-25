"""Context pruning for managing context window."""

from typing import List, Dict, Any
from utilities.token_counter import TokenCounter


class ContextPruner:
    """Prunes context to fit within token limits."""
    
    def __init__(self, token_counter: TokenCounter = None):
        """Initialize the context pruner.
        
        Args:
            token_counter: TokenCounter instance.
        """
        self.token_counter = token_counter or TokenCounter()
    
    def prune(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        preserve_system: bool = True,
        strategy: str = "oldest"
    ) -> List[Dict[str, str]]:
        """Prune messages to fit token limit.
        
        Args:
            messages: List of messages.
            max_tokens: Maximum tokens allowed.
            preserve_system: Keep system message.
            strategy: Pruning strategy (oldest, shortest, relevance).
            
        Returns:
            Pruned messages.
        """
        if not messages:
            return []
        
        system_msg = None
        other_msgs = []
        
        if preserve_system and messages[0].get("role") == "system":
            system_msg = messages[0]
            other_msgs = messages[1:]
        else:
            other_msgs = messages
        
        current_tokens = 0
        if system_msg:
            current_tokens = self.token_counter.count_tokens(system_msg.get("content", ""))
        
        pruned = []
        if system_msg:
            pruned.append(system_msg)
        
        if strategy == "oldest":
            other_msgs = other_msgs[::-1]
        
        for msg in other_msgs:
            msg_tokens = self.token_counter.count_tokens(msg.get("content", ""))
            
            if current_tokens + msg_tokens <= max_tokens:
                pruned.append(msg)
                current_tokens += msg_tokens
            elif strategy == "shortest":
                pass
            else:
                break
        
        if strategy == "oldest":
            pruned = pruned[:1] + pruned[1:][::-1]
        
        return pruned
    
    def smart_prune(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        relevance_scores: Dict[int, float] = None
    ) -> List[Dict[str, str]]:
        """Smart prune with relevance scoring.
        
        Args:
            messages: List of messages.
            max_tokens: Maximum tokens.
            relevance_scores: Message index to relevance score.
            
        Returns:
            Pruned messages.
        """
        if not messages:
            return []
        
        scored_msgs = []
        for i, msg in enumerate(messages):
            if msg.get("role") == "system":
                scored_msgs.append((i, msg, 1.0))
            else:
                score = relevance_scores.get(i, 0.5) if relevance_scores else 0.5
                scored_msgs.append((i, msg, score))
        
        scored_msgs.sort(key=lambda x: x[2], reverse=True)
        
        selected = []
        current_tokens = 0
        
        for idx, msg, score in scored_msgs:
            msg_tokens = self.token_counter.count_tokens(msg.get("content", ""))
            
            if current_tokens + msg_tokens <= max_tokens:
                selected.append((idx, msg))
                current_tokens += msg_tokens
        
        selected.sort(key=lambda x: x[0])
        
        return [msg for idx, msg in selected]
    
    def estimate_compression_ratio(
        self,
        original: List[Dict[str, str]],
        max_tokens: int
    ) -> float:
        """Estimate compression ratio needed.
        
        Args:
            original: Original messages.
            max_tokens: Target token limit.
            
        Returns:
            Compression ratio (0-1).
        """
        original_tokens = self.token_counter.estimate_tokens(original)
        
        if original_tokens <= max_tokens:
            return 1.0
        
        return max_tokens / original_tokens
