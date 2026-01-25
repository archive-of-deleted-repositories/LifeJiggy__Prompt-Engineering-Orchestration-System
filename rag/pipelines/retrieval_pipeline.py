"""Retrieval pipeline for RAG queries."""

from typing import List, Dict, Any, Optional
import logging

from rag.embeddings import EmbeddingEngine
from rag.vector_store import VectorStore
from rag.retrievers.semantic_retriever import SemanticRetriever


class RetrievalPipeline:
    """Handles document retrieval for queries."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize retrieval pipeline.
        
        Args:
            config: Pipeline configuration.
        """
        self.config = config or {}
        self._retrievers = []
        self._reranker = None
        self._embedder = None
        self._vector_store = None
        self._setup_default_components()
    
    def add_retriever(self, retriever) -> None:
        """Add a retriever to the pipeline.
        
        Args:
            retriever: Retriever instance.
        """
        self._retrievers.append(retriever)
    
    def set_reranker(self, reranker) -> None:
        """Set the reranker model.
        
        Args:
            reranker: Reranker instance.
        """
        self._reranker = reranker
    
    def _setup_default_components(self) -> None:
        """Set up default components."""
        # Set up embedder
        embedding_config = self.config.get("embeddings", {})
        self._embedder = EmbeddingEngine(embedding_config)
        
        # Set up vector store
        vector_config = self.config.get("vector_store", {})
        self._vector_store = VectorStore(vector_config)
        
        # Set up default semantic retriever
        semantic_config = self.config.get("semantic_retriever", {})
        semantic_retriever = SemanticRetriever(semantic_config)
        semantic_retriever.set_embedder(self._embedder)
        self._retrievers.append(semantic_retriever)
    
    def set_embedder(self, embedder) -> None:
        """Set embedding model.
        
        Args:
            embedder: Embedder instance.
        """
        self._embedder = embedder
        # Update retrievers with new embedder
        for retriever in self._retrievers:
            if hasattr(retriever, 'set_embedder'):
                retriever.set_embedder(embedder)
    
    def set_vector_store(self, vector_store: VectorStore) -> None:
        """Set vector store and connect retrievers.
        
        Args:
            vector_store: Vector store instance.
        """
        self._vector_store = vector_store
        # Connect retrievers to vector store
        for retriever in self._retrievers:
            if hasattr(retriever, 'connect'):
                retriever.connect(vector_store)
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve documents for a query.
        
        Args:
            query: Query string.
            top_k: Number of results.
            filters: Metadata filters.
            
        Returns:
            List of retrieved documents with scores.
        """
        if not self._retrievers:
            return []
        
        # Connect to vector store if needed
        if self._vector_store:
            self._vector_store.connect()
            self.set_vector_store(self._vector_store)
        
        # Generate query embedding
        query_embedding = None
        if self._embedder:
            query_embedding = await self._embedder.embed(query)
        
        # Retrieve from all retrievers
        all_results = []
        for i, retriever in enumerate(self._retrievers):
            try:
                results = await retriever.retrieve(
                    query=query,
                    query_embedding=query_embedding,
                    top_k=top_k * 2,
                    filters=filters
                )
                
                # Add retriever metadata
                for result in results:
                    result["retriever_index"] = i
                    result["retriever_type"] = retriever.__class__.__name__
                
                all_results.extend(results)
                
            except Exception as e:
                logging.error(f"Error in retriever {i}: {e}")
                continue
        
        # Rerank results if available
        if self._reranker and all_results:
            try:
                all_results = await self._reranker.rerank(query, all_results)
            except Exception as e:
                logging.error(f"Error in reranking: {e}")
        
        # Remove duplicates while preserving order and scores
        seen_contents = set()
        unique_results = []
        for result in all_results:
            content = result.get("content", "")
            if content and content not in seen_contents:
                seen_contents.add(content)
                unique_results.append(result)
        
        # Sort by score (descending) and return top_k
        unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return unique_results[:top_k]
    
    async def hybrid_retrieve(
        self,
        query: str,
        top_k: int = 5,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Perform hybrid retrieval (semantic + keyword).
        
        Args:
            query: Query string.
            top_k: Number of results.
            semantic_weight: Weight for semantic results.
            keyword_weight: Weight for keyword results.
            
        Returns:
            Combined retrieval results.
        """
        # For now, use semantic retrieval
        # TODO: Add keyword retriever for true hybrid search
        return await self.retrieve(query, top_k)
    
    async def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about the retrieval pipeline.
        
        Returns:
            Retrieval statistics.
        """
        stats = {
            "num_retrievers": len(self._retrievers),
            "has_reranker": bool(self._reranker),
            "has_embedder": bool(self._embedder),
            "has_vector_store": bool(self._vector_store),
            "retriever_types": [r.__class__.__name__ for r in self._retrievers]
        }
        
        if self._vector_store:
            try:
                self._vector_store.connect()
                stats["vector_store_count"] = await self._vector_store.get_count()
            except Exception as e:
                logging.error(f"Failed to get vector store stats: {e}")
        
        return stats
