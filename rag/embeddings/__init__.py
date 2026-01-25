"""Embedding engine for generating vector representations."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import time

try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """Generates embeddings for text using sentence-transformers."""
    
    def __init__(self, config: dict = None):
        """Initialize the embedding engine.
        
        Args:
            config: Embedding configuration.
        """
        self.config = config or {}
        self._model = None
        self._model_name = None
        self._device = self.config.get("device", "cpu")
        self._batch_size = self.config.get("batch_size", 32)
        self._loaded = False
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("sentence-transformers not installed. Using fallback embeddings.")
    
    def load_model(self, model_name: str) -> bool:
        """Load an embedding model.
        
        Args:
            model_name: Name of the model to load.
            
        Returns:
            True if successful.
        """
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.warning("Using fallback embedding model")
                self._model_name = model_name
                self._loaded = True
                return True
            
            # Set device
            if self._device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                device = self._device
            
            logger.info(f"Loading sentence transformer model: {model_name}")
            start_time = time.time()
            
            # Load model
            self._model = SentenceTransformer(model_name, device=device)
            self._model_name = model_name
            self._loaded = True
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f}s on device: {device}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {e}")
            return False
    
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed.
            
        Returns:
            Embedding vector.
        """
        if not self._loaded:
            default_model = self.config.get("default_model", "all-MiniLM-L6-v2")
            self.load_model(default_model)
        
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                return self._fallback_embed(text)
            
            # Generate embedding
            embedding = self._model.encode([text], batch_size=1, convert_to_numpy=True)
            return embedding[0].tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed.
            
        Returns:
            List of embedding vectors.
        """
        if not self._loaded:
            default_model = self.config.get("default_model", "all-MiniLM-L6-v2")
            self.load_model(default_model)
        
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                return [self._fallback_embed(text) for text in texts]
            
            # Generate embeddings in batches
            embeddings = self._model.encode(
                texts, 
                batch_size=self._batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[] for _ in texts]
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions.
        
        Returns:
            Dimension size.
        """
        if not self._loaded:
            default_model = self.config.get("default_model", "all-MiniLM-L6-v2")
            self.load_model(default_model)
        
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                return 384  # Fallback dimension
            
            return self._model.get_sentence_embedding_dimension()
            
        except Exception as e:
            logger.error(f"Error getting embedding dimensions: {e}")
            return 0
    
    def _fallback_embed(self, text: str) -> List[float]:
        """Fallback embedding using simple hash-based approach.
        
        Args:
            text: Text to embed.
            
        Returns:
            Simple embedding vector.
        """
        # Simple hash-based embedding for fallback
        import hashlib
        
        # Create a fixed-size embedding (384 dimensions to match MiniLM)
        dimensions = 384
        embedding = [0.0] * dimensions
        
        # Use text hash to generate pseudo-random values
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        for i, char in enumerate(text_hash):
            if i >= dimensions:
                break
            # Convert hex character to float between -1 and 1
            val = int(char, 16) / 15.0 * 2 - 1
            embedding[i] = val
        
        return embedding
    
    async def embed_with_metadata(
        self, 
        texts: List[str], 
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Generate embeddings with metadata.
        
        Args:
            texts: List of texts to embed.
            metadata: Optional metadata for each text.
            
        Returns:
            List of embeddings with metadata.
        """
        embeddings = await self.embed_batch(texts)
        
        results = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            result = {
                "text": text,
                "embedding": embedding,
                "model": self._model_name,
                "dimensions": len(embedding)
            }
            
            if metadata and i < len(metadata):
                result["metadata"] = metadata[i]
            
            results.append(result)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model.
        
        Returns:
            Model information.
        """
        if not self._loaded:
            return {"loaded": False}
        
        info = {
            "loaded": True,
            "model_name": self._model_name,
            "device": self._device,
            "batch_size": self._batch_size,
            "dimensions": self.get_dimensions()
        }
        
        if SENTENCE_TRANSFORMERS_AVAILABLE and self._model:
            info.update({
                "max_seq_length": getattr(self._model, "max_seq_length", None),
                "modules": list(self._model._modules.keys()) if hasattr(self._model, "_modules") else []
            })
        
        return info
    
    async def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
        embeddings = await self.embed_batch([text1, text2])
        
        if len(embeddings) != 2 or not embeddings[0] or not embeddings[1]:
            return 0.0
        
        # Calculate cosine similarity
        return self._cosine_similarity(embeddings[0], embeddings[1])
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector.
            vec2: Second vector.
            
        Returns:
            Cosine similarity score.
        """
        try:
            import numpy as np
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
            
        except ImportError:
            # Fallback without numpy
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
