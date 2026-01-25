"""Incremental summarizer for ongoing conversations."""

from typing import List, Dict, Any
from context_management.memory import ShortTermMemory


class IncrementalSummarizer:
    """Incrementally summarizes conversations."""
    
    def __init__(self, window_size: int = 10, summary_interval: int = 5):
        """Initialize the incremental summarizer.
        
        Args:
            window_size: Messages before summarization.
            summary_interval: Messages between summaries.
        """
        self.window_size = window_size
        self.summary_interval = summary_interval
        self._message_count = 0
        self._current_summary = ""
        self._window_memory = ShortTermMemory(max_messages=window_size)
    
    def add_message(self, message: Dict[str, str]) -> str:
        """Add a message and potentially summarize.
        
        Args:
            message: Message to add.
            
        Returns:
            Updated summary if generated.
        """
        self._window_memory.add(message)
        self._message_count += 1
        
        if self._message_count % self.summary_interval == 0:
            return self._generate_summary()
        
        return ""
    
    def add_messages(self, messages: List[Dict[str, str]]) -> str:
        """Add multiple messages.
        
        Args:
            messages: Messages to add.
            
        Returns:
            Updated summary if generated.
        """
        summary = ""
        for msg in messages:
            summary = self.add_message(msg)
        return summary
    
    def _generate_summary(self) -> str:
        """Generate summary from current window."""
        messages = self._window_memory.get_all()
        
        if not messages:
            return ""
        
        user_msgs = [m for m in messages if m.get("role") == "user"]
        topics = []
        for msg in user_msgs:
            content = msg.get("content", "")
            words = content.split()[:3]
            if words:
                topics.append(" ".join(words))
        
        new_summary = f"Recent topics: {', '.join(topics[-5:])}"
        
        if self._current_summary:
            self._current_summary = f"{self._current_summary} | {new_summary}"
        else:
            self._current_summary = new_summary
        
        self._window_memory.clear()
        
        return self._current_summary
    
    def get_summary(self) -> str:
        """Get current summary.
        
        Returns:
            Current summary.
        """
        return self._current_summary
    
    def reset(self) -> None:
        """Reset the summarizer."""
        self._message_count = 0
        self._current_summary = ""
        self._window_memory.clear()
