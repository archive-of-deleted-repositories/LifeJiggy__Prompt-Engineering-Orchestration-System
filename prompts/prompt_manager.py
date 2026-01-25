"""Prompt manager for handling prompt operations."""


class PromptManager:
    """Manages prompt templates and versions."""
    
    def __init__(self, prompts_dir: str = "./prompts"):
        """Initialize the prompt manager.
        
        Args:
            prompts_dir: Directory containing prompt templates.
        """
        self.prompts_dir = prompts_dir
        self._prompts = {}
    
    def load_prompt(self, prompt_id: str) -> dict:
        """Load a prompt by ID.
        
        Args:
            prompt_id: Unique identifier for the prompt.
            
        Returns:
            Prompt data dictionary.
        """
        return self._prompts.get(prompt_id, {})
    
    def save_prompt(self, prompt_id: str, prompt_data: dict) -> bool:
        """Save a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt.
            prompt_data: Prompt data to save.
            
        Returns:
            True if successful.
        """
        self._prompts[prompt_id] = prompt_data
        return True
    
    def list_prompts(self) -> list[str]:
        """List all available prompts.
        
        Returns:
            List of prompt IDs.
        """
        return list(self._prompts.keys())
