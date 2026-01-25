"""Semantic search retriever implementation."""

from typing import List, Dict, Any, Optional
import numpy as np


class SemanticRetriever:
    """Semantic search using vector similarity."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the semantic retriever.
        
        Args:
            config: Retriever configuration.
        """
        self.config = config or {}
        self._vector_store = None
        self._embedder = None
    
    def connect(self, vector_store) -> None:
        """Connect to vector store.
        
        Args:
            vector_store: VectorStore instance.
        """
        self._vector_store = vector_store
    
    def set_embedder(self, embedder) -> None:
        """Set the embedder.
        
        Args:
            embedder: Embedding instance.
        """
        self._embedder = embedder
    
    async def retrieve(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search.
        
        Args:
            query: Query string.
            query_embedding: Pre-computed query embedding.
            top_k: Number of results.
            filters: Metadata filters.
            
        Returns:
            List of search results.
        """
        if not self._vector_store:
            return []
        
        if query_embedding is None and self._embedder:
            query_embedding = await self._embedder.embed(query)
        
        if query_embedding is None:
            return []
        
        results = self._vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        return [
            {
                "id": r.get("id", ""),
                "content": r.get("content", ""),
                "score": 1.0 - r.get("distance", 0.0),
                "metadata": r.get("metadata", {}),
                "retriever": "semantic"
            }
            for r in results
        ]
