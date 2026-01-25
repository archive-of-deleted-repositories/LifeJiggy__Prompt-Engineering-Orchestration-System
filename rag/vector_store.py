"""Vector store implementation with ChromaDB."""

import asyncio
import uuid
from typing import List, Dict, Any, Optional
import logging

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector database for document storage and retrieval using ChromaDB."""
    
    def __init__(self, config: dict = None):
        """Initialize the vector store.
        
        Args:
            config: Vector store configuration.
        """
        self.config = config or {}
        self._client = None
        self._collection = None
        self._connected = False
        
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not installed. Vector store will use in-memory fallback.")
    
    def connect(self) -> bool:
        """Connect to the vector database.
        
        Returns:
            True if successful.
        """
        try:
            if not CHROMADB_AVAILABLE:
                logger.info("Using in-memory vector store fallback")
                self._store = {}
                self._connected = True
                return True
            
            persist_directory = self.config.get("persist_path", "./data/vector_db")
            collection_name = self.config.get("collection", "documents")
            
            # Configure ChromaDB settings
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory,
                anonymized_telemetry=False
            )
            
            # Create client
            self._client = chromadb.PersistentClient(settings=settings)
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            self._connected = True
            logger.info(f"Connected to ChromaDB collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to vector store: {e}")
            # Fallback to in-memory store
            self._store = {}
            self._connected = True
            return True
    
    def disconnect(self) -> None:
        """Disconnect from the vector database."""
        if self._client and CHROMADB_AVAILABLE:
            try:
                self._client = None
                self._collection = None
                self._connected = False
                logger.info("Disconnected from ChromaDB")
            except Exception as e:
                logger.error(f"Error disconnecting from vector store: {e}")
    
    async def add(
        self, 
        documents: List[str], 
        embeddings: List[List[float]], 
        metadata: List[Dict[str, Any]] = None
    ) -> List[str]:
        """Add documents to the store.
        
        Args:
            documents: Document strings.
            embeddings: Document embeddings.
            metadata: Optional metadata.
            
        Returns:
            List of document IDs.
        """
        if not self._connected:
            await self.connect()
        
        try:
            if not CHROMADB_AVAILABLE or self._collection is None:
                # Fallback to in-memory storage
                doc_ids = []
                for i, (doc, emb) in enumerate(zip(documents, embeddings)):
                    doc_id = str(uuid.uuid4())
                    self._store[doc_id] = {
                        "document": doc,
                        "embedding": emb,
                        "metadata": metadata[i] if metadata and i < len(metadata) else {}
                    }
                    doc_ids.append(doc_id)
                return doc_ids
            
            # Generate document IDs
            doc_ids = [str(uuid.uuid4()) for _ in documents]
            
            # Prepare metadata
            if metadata is None:
                metadata = [{} for _ in documents]
            
            # Add to ChromaDB
            self._collection.add(
                ids=doc_ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadata
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return []
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector.
            top_k: Number of results.
            filters: Optional metadata filters.
            
        Returns:
            List of matching documents with scores.
        """
        if not self._connected:
            await self.connect()
        
        try:
            if not CHROMADB_AVAILABLE or self._collection is None:
                # Fallback to in-memory search
                results = []
                for doc_id, data in self._store.items():
                    # Simple cosine similarity
                    doc_emb = data["embedding"]
                    similarity = self._cosine_similarity(query_embedding, doc_emb)
                    
                    # Apply filters if provided
                    if filters:
                        match = True
                        for key, value in filters.items():
                            if data["metadata"].get(key) != value:
                                match = False
                                break
                        if not match:
                            continue
                    
                    results.append({
                        "id": doc_id,
                        "document": data["document"],
                        "metadata": data["metadata"],
                        "score": similarity
                    })
                
                # Sort by similarity and return top_k
                results.sort(key=lambda x: x["score"], reverse=True)
                return results[:top_k]
            
            # Build query
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": top_k
            }
            
            if filters:
                query_params["where"] = filters
            
            # Query ChromaDB
            results = self._collection.query(**query_params)
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": results["distances"][0][i] if "distances" in results else 0.0
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    async def delete(self, doc_ids: List[str]) -> bool:
        """Delete documents from the store.
        
        Args:
            doc_ids: Document IDs to delete.
            
        Returns:
            True if successful.
        """
        if not self._connected:
            await self.connect()
        
        try:
            if not CHROMADB_AVAILABLE or self._collection is None:
                # Fallback to in-memory deletion
                for doc_id in doc_ids:
                    self._store.pop(doc_id, None)
                return True
            
            # Delete from ChromaDB
            self._collection.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents from vector store: {e}")
            return False
    
    async def get_count(self) -> int:
        """Get the number of documents in the store.
        
        Returns:
            Document count.
        """
        if not self._connected:
            await self.connect()
        
        try:
            if not CHROMADB_AVAILABLE or self._collection is None:
                return len(self._store)
            
            count = self._collection.count()
            return count
            
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
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
            
            return dot_product / (norm1 * norm2)
            
        except ImportError:
            # Fallback without numpy
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID.
        
        Args:
            doc_id: Document ID.
            
        Returns:
            Document data or None if not found.
        """
        if not self._connected:
            await self.connect()
        
        try:
            if not CHROMADB_AVAILABLE or self._collection is None:
                return self._store.get(doc_id)
            
            result = self._collection.get(ids=[doc_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0],
                    "metadata": result["metadatas"][0] if result["metadatas"] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
