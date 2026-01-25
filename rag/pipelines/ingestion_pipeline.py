"""Ingestion pipeline for document processing."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import asyncio
import os
from pathlib import Path

from rag.embeddings import EmbeddingEngine
from rag.chunking import (
    FixedSizeChunker, 
    RecursiveCharacterChunker, 
    SemanticChunker, 
    MarkdownChunker
)
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document model for RAG."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class IngestionPipeline:
    """Handles document ingestion into the RAG system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the ingestion pipeline.
        
        Args:
            config: Pipeline configuration.
        """
        self.config = config or {}
        self._chunkers = {}
        self._embedder = None
        self._vector_store = None
        self._setup_default_components()
    
    def _setup_default_components(self) -> None:
        """Set up default chunkers and embedder."""
        chunker_config = self.config.get("chunking", {})
        
        # Register default chunkers
        self._chunkers["fixed"] = FixedSizeChunker(chunker_config.get("fixed", {}))
        self._chunkers["recursive"] = RecursiveCharacterChunker(chunker_config.get("recursive", {}))
        self._chunkers["markdown"] = MarkdownChunker(chunker_config.get("markdown", {}))
        self._chunkers["semantic"] = SemanticChunker(chunker_config.get("semantic", {}))
        
        # Set up embedder
        embedding_config = self.config.get("embeddings", {})
        self._embedder = EmbeddingEngine(embedding_config)
        
        # Set up vector store
        vector_config = self.config.get("vector_store", {})
        self._vector_store = VectorStore(vector_config)
    
    def add_chunker(self, name: str, chunker) -> None:
        """Register a chunker.
        
        Args:
            name: Chunker name.
            chunker: Chunker instance.
        """
        self._chunkers[name] = chunker
    
    def set_embedder(self, embedder) -> None:
        """Set the embedding model.
        
        Args:
            embedder: Embedder instance.
        """
        self._embedder = embedder
    
    def set_vector_store(self, vector_store: VectorStore) -> None:
        """Set the vector store.
        
        Args:
            vector_store: Vector store instance.
        """
        self._vector_store = vector_store
    
    async def ingest(
        self,
        documents: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
        chunker: str = "recursive",
        store: bool = True
    ) -> List[Document]:
        """Ingest documents into the system.
        
        Args:
            documents: List of document texts.
            metadata: Optional metadata for each document.
            chunker: Chunker to use.
            store: Whether to store in vector store.
            
        Returns:
            List of processed documents.
        """
        logger.info(f"Starting ingestion of {len(documents)} documents using {chunker} chunker")
        
        # Get chunker
        chunker_obj = self._chunkers.get(chunker)
        if not chunker_obj:
            logger.warning(f"Chunker '{chunker}' not found, using recursive chunker")
            chunker_obj = self._chunkers.get("recursive")
        
        # Set embedder for semantic chunker
        if chunker == "semantic" and chunker_obj and hasattr(chunker_obj, 'set_embedder'):
            chunker_obj.set_embedder(self._embedder)
        
        results = []
        total_chunks = 0
        
        for i, doc in enumerate(documents):
            doc_metadata = metadata[i] if metadata and i < len(metadata) else {}
            
            # Add document index to metadata
            doc_metadata["doc_index"] = i
            doc_metadata["total_docs"] = len(documents)
            
            # Chunk the document
            if chunker_obj:
                chunks = chunker_obj.chunk(doc)
            else:
                chunks = [doc]
            logger.debug(f"Document {i} chunked into {len(chunks)} chunks")
            
            for j, chunk in enumerate(chunks):
                chunk_metadata = {
                    **doc_metadata,
                    "chunk_index": j,
                    "total_chunks": len(chunks),
                    "chunker": chunker,
                    "char_count": len(chunk)
                }
                
                doc_obj = Document(
                    id=f"doc_{i}_chunk_{j}_{hash(chunk) % 1000000}",
                    content=chunk,
                    metadata=chunk_metadata,
                )
                results.append(doc_obj)
                total_chunks += 1
        
        # Generate embeddings
        if self._embedder and results:
            logger.info(f"Generating embeddings for {len(results)} chunks")
            try:
                contents = [d.content for d in results]
                embeddings = await self._embedder.embed_batch(contents)
                
                for doc, emb in zip(results, embeddings):
                    doc.embedding = emb
                
                logger.info("Embeddings generated successfully")
            except Exception as e:
                logger.error(f"Failed to generate embeddings: {e}")
        
        # Store in vector store
        if store and self._vector_store and results:
            logger.info(f"Storing {len(results)} chunks in vector store")
            try:
                connected = self._vector_store.connect()
                if connected:
                    # Prepare data for storage
                    doc_texts = [d.content for d in results]
                    doc_embeddings = [d.embedding for d in results if d.embedding]
                    doc_metadata = [d.metadata for d in results]
                    
                    # Store if we have embeddings
                    if doc_embeddings:
                        stored_ids = await self._vector_store.add(
                            documents=doc_texts,
                            embeddings=doc_embeddings,
                            metadata=doc_metadata
                        )
                        logger.info(f"Successfully stored {len(stored_ids)} chunks in vector store")
                    else:
                        logger.warning("No embeddings generated, skipping vector store storage")
                else:
                    logger.error("Failed to connect to vector store")
                    
            except Exception as e:
                logger.error(f"Failed to store documents in vector store: {e}")
        
        logger.info(f"Ingestion completed: {total_chunks} chunks from {len(documents)} documents")
        return results
    
    async def ingest_file(
        self,
        filepath: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunker: str = "recursive",
        store: bool = True
    ) -> List[Document]:
        """Ingest a file.
        
        Args:
            filepath: Path to the file.
            metadata: File metadata.
            chunker: Chunker to use.
            store: Whether to store in vector store.
            
        Returns:
            List of processed documents.
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            # Read file content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine file type for appropriate chunking
            file_ext = path.suffix.lower()
            if file_ext in ['.md', '.markdown']:
                chunker = 'markdown'
            
            file_metadata = {
                "source": str(path.absolute()),
                "filename": path.name,
                "file_extension": file_ext,
                "file_size": path.stat().st_size,
                "chunker": chunker,
                **(metadata or {})
            }
            
            logger.info(f"Ingesting file: {filepath} ({len(content)} chars)")
            return await self.ingest(
                documents=[content],
                metadata=[file_metadata],
                chunker=chunker,
                store=store
            )
            
        except Exception as e:
            logger.error(f"Failed to ingest file {filepath}: {e}")
            raise
    
    async def ingest_directory(
        self,
        directory: str,
        pattern: str = "*.txt",
        recursive: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        chunker: str = "recursive",
        store: bool = True
    ) -> List[Document]:
        """Ingest all files in a directory.
        
        Args:
            directory: Directory path.
            pattern: File pattern to match.
            recursive: Whether to search recursively.
            metadata: Additional metadata for all files.
            chunker: Chunker to use.
            store: Whether to store in vector store.
            
        Returns:
            List of processed documents.
        """
        path = Path(directory)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        # Find files
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        if not files:
            logger.warning(f"No files found matching pattern '{pattern}' in {directory}")
            return []
        
        logger.info(f"Found {len(files)} files to ingest in {directory}")
        
        all_documents = []
        
        for file_path in files:
            try:
                if file_path.is_file():
                    file_metadata = {
                        "directory": str(path.absolute()),
                        "relative_path": str(file_path.relative_to(path)),
                        **(metadata or {})
                    }
                    
                    documents = await self.ingest_file(
                        str(file_path),
                        metadata=file_metadata,
                        chunker=chunker,
                        store=store
                    )
                    all_documents.extend(documents)
                    
            except Exception as e:
                logger.error(f"Failed to ingest file {file_path}: {e}")
                continue
        
        logger.info(f"Directory ingestion completed: {len(all_documents)} chunks from {len(files)} files")
        return all_documents
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics.
        
        Returns:
            Statistics about the ingestion pipeline.
        """
        stats = {
            "available_chunkers": list(self._chunkers.keys()),
            "embedder_loaded": bool(self._embedder),
            "vector_store_connected": bool(self._vector_store and self._vector_store._connected),
        }
        
        if self._embedder:
            stats["embedder_info"] = self._embedder.get_model_info()
        
        if self._vector_store:
            try:
                connected = self._vector_store.connect()
                if connected:
                    stats["vector_store_count"] = await self._vector_store.get_count()
            except Exception as e:
                logger.error(f"Failed to get vector store stats: {e}")
        
        return stats
