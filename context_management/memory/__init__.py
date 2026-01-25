"""Memory implementations for context management."""


class ShortTermMemory:
    """Short-term conversation memory."""
    
    def __init__(self, max_messages: int = 20):
        """Initialize short-term memory.
        
        Args:
            max_messages: Maximum number of messages to retain.
        """
        self.max_messages = max_messages
        self._messages = []
    
    def add(self, message: dict) -> None:
        """Add a message to memory.
        
        Args:
            message: Message to add.
        """
        self._messages.append(message)
        if len(self._messages) > self.max_messages:
            self._messages.pop(0)
    
    def get_all(self) -> list[dict]:
        """Get all messages.
        
        Returns:
            List of messages.
        """
        return self._messages.copy()
    
    def clear(self) -> None:
        """Clear all messages."""
        self._messages = []
    
    def get_count(self) -> int:
        """Get message count.
        
        Returns:
            Number of messages.
        """
        return len(self._messages)


class LongTermMemory:
    """Long-term persistent user memory."""
    
    def __init__(self, storage_path: str = "./data/long_term"):
        """Initialize long-term memory.
        
        Args:
            storage_path: Path to storage directory.
        """
        self.storage_path = storage_path
        self._facts = {}
    
    def add_fact(self, user_id: str, fact: str, metadata: dict = None) -> bool:
        """Add a fact for a user.
        
        Args:
            user_id: User identifier.
            fact: Fact to store.
            metadata: Optional metadata.
            
        Returns:
            True if successful.
        """
        if user_id not in self._facts:
            self._facts[user_id] = []
        self._facts[user_id].append({"fact": fact, "metadata": metadata or {}})
        return True
    
    def get_facts(self, user_id: str) -> list[dict]:
        """Get all facts for a user.
        
        Args:
            user_id: User identifier.
            
        Returns:
            List of facts with metadata.
        """
        return self._facts.get(user_id, [])
    
    def search_facts(self, user_id: str, query: str) -> list[dict]:
        """Search facts for a user.
        
        Args:
            user_id: User identifier.
            query: Search query.
            
        Returns:
            Matching facts.
        """
        return []


class SemanticMemory:
    """Semantic knowledge graph for concept relationships."""
    
    def __init__(self, config: dict = None):
        """Initialize semantic memory.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
        self._graph = {}
    
    def add_concept(self, concept: str, relationships: list[dict]) -> bool:
        """Add a concept with relationships.
        
        Args:
            concept: Concept name.
            relationships: List of related concepts.
            
        Returns:
            True if successful.
        """
        self._graph[concept] = relationships
        return True
    
    def get_related(self, concept: str) -> list[dict]:
        """Get concepts related to a given concept.
        
        Args:
            concept: Concept to search.
            
        Returns:
            List of related concepts.
        """
        return self._graph.get(concept, [])
    
    def search(self, query: str) -> list[str]:
        """Search for concepts.
        
        Args:
            query: Search query.
            
        Returns:
            Matching concepts.
        """
        return []
