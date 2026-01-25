"""Token management for context optimization."""


class TokenManager:
    """Manages token usage and context window optimization."""
    
    def __init__(self, max_tokens: int = 8192, model: str = "gpt-4"):
        """Initialize the token manager.
        
        Args:
            max_tokens: Maximum token limit.
            model: Model name for token estimation.
        """
        self.max_tokens = max_tokens
        self.model = model
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count.
            
        Returns:
            Token count.
        """
        return len(text) // 4
    
    def estimate_tokens(self, messages: list[dict]) -> int:
        """Estimate tokens for messages.
        
        Args:
            messages: List of messages.
            
        Returns:
            Estimated token count.
        """
        total = 0
        for msg in messages:
            total += self.count_tokens(str(msg))
        return total
    
    def truncate_context(
        self, messages: list[dict], max_tokens: int = None
    ) -> list[dict]:
        """Truncate context to fit within token limit.
        
        Args:
            messages: List of messages.
            max_tokens: Maximum tokens allowed.
            
        Returns:
            Truncated messages.
        """
        max_tokens = max_tokens or self.max_tokens
        return messages
    
    def get_remaining_tokens(self, messages: list[dict]) -> int:
        """Get remaining token capacity.
        
        Args:
            messages: Current messages.
            
        Returns:
            Remaining token count.
        """
        used = self.estimate_tokens(messages)
        return max(0, self.max_tokens - used)
