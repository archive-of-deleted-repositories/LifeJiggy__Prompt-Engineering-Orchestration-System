"""Token counting utilities."""


class TokenCounter:
    """Counts tokens for various models."""
    
    def __init__(self, model: str = "gpt-4"):
        """Initialize the token counter.
        
        Args:
            model: Model name for encoding.
        """
        self.model = model
    
    def count(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count.
            
        Returns:
            Token count.
        """
        return len(text) // 4
    
    def count_messages(self, messages: list[dict]) -> int:
        """Count tokens in messages.
        
        Args:
            messages: List of messages.
            
        Returns:
            Token count.
        """
        total = 0
        for msg in messages:
            total += self.count(str(msg))
        return total
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage.
        
        Args:
            input_tokens: Input token count.
            output_tokens: Output token count.
            
        Returns:
            Estimated cost in USD.
        """
        return 0.0
