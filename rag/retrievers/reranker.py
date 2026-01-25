"""Cross-encoder reranker implementation."""

import asyncio
from typing import List, Dict, Any, Optional
import logging

try:
    from sentence_transformers import CrossEncoder
    import torch
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False

logger = logging.getLogger(__name__)


class Reranker:
    """Cross-encoder based document reranker with fallback."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize cross-encoder reranker.
        
        Args:
            config: Reranker configuration.
        """
        self.config = config or {}
        self._model = None
        self._model_name = None
        self._batch_size = self.config.get("batch_size", 16)
        self._device = self.config.get("device", "cpu")
        self._loaded = False
        
        if not CROSS_ENCODER_AVAILABLE:
            logger.warning("sentence-transformers cross-encoder not available, using fallback")
    
    def load_model(self, model_name: str) -> bool:
        """Load cross-encoder model.
        
        Args:
            model_name: Name of cross-encoder model.
            
        Returns:
            True if successful.
        """
        try:
            if not CROSS_ENCODER_AVAILABLE:
                logger.warning("Cross-encoder not available, using fallback")
                self._model_name = model_name
                self._loaded = True
                return True
            
            # Set device
            if self._device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                device = self._device
            
            logger.info(f"Loading cross-encoder model: {model_name}")
            self._model = CrossEncoder(model_name, device=device)
            self._model_name = model_name
            self._loaded = True
            
            logger.info(f"Cross-encoder loaded on device: {device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load cross-encoder {model_name}: {e}")
            return False
    
    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Rerank documents based on query relevance.
        
        Args:
            query: Query string.
            documents: List of document dictionaries.
            top_k: Number of documents to return.
            
        Returns:
            Reranked list of documents.
        """
        if not documents:
            return []
        
        if not self._loaded:
            default_model = self.config.get("default_model", "cross-encoder/ms-marco-MiniLM-L-6-v2")
            self.load_model(default_model)
        
        try:
            if not CROSS_ENCODER_AVAILABLE or self._model is None:
                return self._fallback_rerank(query, documents, top_k)
            
            # Prepare query-document pairs
            pairs = [[query, doc.get("content", doc.get("text", ""))] for doc in documents]
            
            # Get relevance scores
            scores = self._model.predict(pairs)
            
            # Combine with original documents
            reranked_docs = []
            for doc, score in zip(documents, scores):
                reranked_doc = doc.copy()
                reranked_doc["rerank_score"] = float(score)
                reranked_docs.append(reranked_doc)
            
            # Sort by rerank score
            reranked_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
            
            # Return top_k if specified
            if top_k:
                reranked_docs = reranked_docs[:top_k]
            
            # Add position information
            for i, doc in enumerate(reranked_docs):
                doc["rerank_position"] = i + 1
            
            return reranked_docs
            
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            return self._fallback_rerank(query, documents, top_k)
    
    def _fallback_rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fallback reranking using enhanced keyword overlap and original scores.
        
        Args:
            query: Query string.
            documents: List of document dictionaries.
            top_k: Number of documents to return.
            
        Returns:
            Reranked list of documents.
        """
        query_terms = set(query.lower().split())
        
        reranked_docs = []
        for doc in documents:
            content = doc.get("content", doc.get("text", "")).lower()
            content_terms = set(content.split())
            
            # Enhanced overlap scoring
            overlap = len(query_terms.intersection(content_terms))
            coverage = overlap / len(query_terms) if query_terms else 0
            density = overlap / len(content_terms) if content_terms else 0
            
            # Combine with original score
            original_score = doc.get("score", 0.0)
            new_score = (original_score * 0.4) + (coverage * 0.3) + (density * 0.3)
            
            reranked_doc = doc.copy()
            reranked_doc["rerank_score"] = new_score
            reranked_docs.append(reranked_doc)
        
        # Sort by fallback score
        reranked_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        if top_k:
            reranked_docs = reranked_docs[:top_k]
        
        # Add position information
        for i, doc in enumerate(reranked_docs):
            doc["rerank_position"] = i + 1
        
        return reranked_docs
    
    def diversify(
        self,
        documents: List[Dict[str, Any]],
        max_per_source: int = 2,
        diversity_field: str = "source"
    ) -> List[Dict[str, Any]]:
        """Diversify results by specified field.
        
        Args:
            documents: List of documents.
            max_per_source: Maximum documents per source.
            diversity_field: Field to use for diversification.
            
        Returns:
            Diversified document list.
        """
        field_counts = {}
        diversified = []
        
        for doc in documents:
            field_value = doc.get("metadata", {}).get(diversity_field, "unknown")
            
            if field_value not in field_counts:
                field_counts[field_value] = 0
            
            if field_counts[field_value] < max_per_source:
                diversified.append(doc)
                field_counts[field_value] += 1
        
        return diversified
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.
        
        Returns:
            Model information dictionary.
        """
        if not self._loaded:
            return {"loaded": False}
        
        info = {
            "loaded": True,
            "model_name": self._model_name,
            "device": self._device,
            "batch_size": self._batch_size
        }
        
        if CROSS_ENCODER_AVAILABLE and self._model:
            info.update({
                "max_seq_length": getattr(self._model, "max_seq_length", None),
                "num_labels": getattr(self._model, "num_labels", 1),
                "has_config": hasattr(self._model, "config")
            })
        
        return info
