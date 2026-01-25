"""Vector store schema definitions."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VectorDocument:
    """Document stored in vector database."""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VectorIndex:
    """Vector index metadata."""
    name: str
    dimension: int
    metric: str = "cosine"
    engine: str = "hnsw"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Search result from vector database."""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


class VectorStoreSchema:
    """Schema definitions for vector store."""
    
    COLLECTIONS = {
        "documents": {
            "description": "Main document collection",
            "fields": {
                "id": {"type": "string", "primary": True},
                "content": {"type": "string"},
                "embedding": {"type": "vector", "dimension": 1536},
                "metadata": {"type": "json"},
                "created_at": {"type": "datetime"},
                "updated_at": {"type": "datetime"},
            },
            "indexes": ["content.text", "metadata.json"]
        },
        "memories": {
            "description": "User memories and facts",
            "fields": {
                "id": {"type": "string", "primary": True},
                "user_id": {"type": "string", "index": True},
                "content": {"type": "string"},
                "embedding": {"type": "vector", "dimension": 768},
                "memory_type": {"type": "string"},
                "importance": {"type": "float"},
                "created_at": {"type": "datetime"},
            }
        },
        "conversations": {
            "description": "Conversation summaries",
            "fields": {
                "id": {"type": "string", "primary": True},
                "session_id": {"type": "string", "index": True},
                "summary": {"type": "string"},
                "embedding": {"type": "vector", "dimension": 768},
                "message_count": {"type": "int"},
                "created_at": {"type": "datetime"},
            }
        }
    }
    
    @classmethod
    def get_collection_schema(cls, collection: str) -> Dict[str, Any]:
        """Get schema for a collection."""
        return cls.COLLECTIONS.get(collection, {})
    
    @classmethod
    def validate_document(cls, collection: str, document: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate a document against its collection schema."""
        schema = cls.get_collection_schema(collection)
        if not schema:
            return True, []
        
        errors = []
        required_fields = []
        
        for field_name, field_config in schema.get("fields", {}).items():
            if field_config.get("primary", False):
                required_fields.append(field_name)
        
        for field_name in required_fields:
            if field_name not in document:
                errors.append(f"Missing required field: {field_name}")
        
        return len(errors) == 0, errors
