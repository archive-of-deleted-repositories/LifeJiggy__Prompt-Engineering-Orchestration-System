"""Augmentation pipeline for prompt augmentation."""

from typing import List, Dict, Any, Optional


class AugmentationPipeline:
    """Augments prompts with retrieved context."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the augmentation pipeline.
        
        Args:
            config: Pipeline configuration.
        """
        self.config = config or {}
        self._retrieval_pipeline = None
    
    def set_retrieval_pipeline(self, pipeline) -> None:
        """Set the retrieval pipeline.
        
        Args:
            pipeline: RetrievalPipeline instance.
        """
        self._retrieval_pipeline = pipeline
    
    async def augment(
        self,
        query: str,
        system_prompt: str = "",
        retrieved_docs: Optional[List[Dict[str, Any]]] = None,
        max_context_tokens: int = 4000
    ) -> Dict[str, Any]:
        """Augment a query with retrieved context.
        
        Args:
            query: Original query.
            system_prompt: System prompt to augment.
            retrieved_docs: Pre-retrieved documents.
            max_context_tokens: Maximum context tokens.
            
        Returns:
            Augmented prompt and metadata.
        """
        if retrieved_docs is None and self._retrieval_pipeline:
            retrieved_docs = await self._retrieval_pipeline.retrieve(
                query=query,
                top_k=5
            )
        
        context_parts = []
        sources = []
        
        for doc in retrieved_docs:
            content = doc.get("content", "")
            source = doc.get("metadata", {}).get("source", "unknown")
            
            context_parts.append(f"[Source: {source}]\n{content}")
            sources.append({
                "content": content,
                "source": source,
                "score": doc.get("score", 0.0)
            })
        
        context_text = "\n\n".join(context_parts)
        
        if system_prompt:
            augmented_system = f"""{system_prompt}

## Retrieved Context

Use the following information to inform your response:

{context_text}

If the retrieved context is relevant to the user's query, incorporate it into your answer. If not, rely on your general knowledge.
"""
        else:
            augmented_system = f"""You are a helpful AI assistant. Use the following retrieved context to answer the user's question.

## Retrieved Context

{context_text}

Answer the user's question based on the retrieved context above. If the context doesn't contain relevant information, say so.
"""
        return {
            "augmented_system": augmented_system,
            "user_query": query,
            "context_length": len(context_text),
            "num_sources": len(sources),
            "sources": sources
        }
    
    async def create_augmented_messages(
        self,
        query: str,
        system_prompt: str,
        retrieved_docs: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Create message list with augmented context.
        
        Args:
            query: Current user query.
            system_prompt: System prompt.
            retrieved_docs: Retrieved documents.
            conversation_history: Previous messages.
            
        Returns:
            List of messages for the model.
        """
        augmentation = await self.augment(
            query=query,
            system_prompt=system_prompt,
            retrieved_docs=retrieved_docs
        )
        
        messages = [
            {"role": "system", "content": augmentation["augmented_system"]}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": query})
        
        return messages
