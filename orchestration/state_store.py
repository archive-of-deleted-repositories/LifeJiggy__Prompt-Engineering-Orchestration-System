"""State management for workflows."""


class StateStore:
    """Persistent state storage for workflows."""
    
    def __init__(self, storage_path: str = "./data/state"):
        """Initialize the state store.
        
        Args:
            storage_path: Path to state storage.
        """
        self.storage_path = storage_path
        self._states = {}
    
    def save_state(self, session_id: str, state: dict) -> bool:
        """Save workflow state.
        
        Args:
            session_id: Session identifier.
            state: State to save.
            
        Returns:
            True if successful.
        """
        self._states[session_id] = state
        return True
    
    def load_state(self, session_id: str) -> dict:
        """Load workflow state.
        
        Args:
            session_id: Session identifier.
            
        Returns:
            Saved state or empty dict.
        """
        return self._states.get(session_id, {})
    
    def delete_state(self, session_id: str) -> bool:
        """Delete workflow state.
        
        Args:
            session_id: Session identifier.
            
        Returns:
            True if successful.
        """
        if session_id in self._states:
            del self._states[session_id]
            return True
        return False
    
    def list_states(self) -> list[str]:
        """List all state sessions.
        
        Returns:
            List of session IDs.
        """
        return list(self._states.keys())
