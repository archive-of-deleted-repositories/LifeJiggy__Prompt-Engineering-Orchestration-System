"""RAG configuration for chunking, embeddings, and retrieval."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ChunkingConfig(BaseModel):
    """Configuration for document chunking."""
    strategy: str = "semantic"
    chunk_size: int = 1000
    chunk_overlap: int = 100
    separator: str = "\n"
    max_chunks: int = 100


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings."""
    model: str = "text-embedding-3-small"
    dimensions: int = 1536
    batch_size: int = 32
    provider: str = "openai"


class RetrievalConfig(BaseModel):
    """Configuration for retrieval."""
    top_k: int = 5
    similarity_threshold: float = 0.7
    use_reranker: bool = True
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"
    hybrid_alpha: float = 0.5


class RAGConfig(BaseModel):
    """Main RAG configuration."""
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            "chunking": self.chunking.model_dump(),
            "embedding": self.embedding.model_dump(),
            "retrieval": self.retrieval.model_dump(),
        }
    
    @classmethod
    def from_yaml(cls, filepath: str) -> "RAGConfig":
        """Load configuration from YAML file."""
        import yaml
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
