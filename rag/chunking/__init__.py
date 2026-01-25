"""Chunking strategies for document processing."""

import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Chunker:
    """Base chunker interface."""
    
    def __init__(self, config: dict = None):
        """Initialize chunker.
        
        Args:
            config: Chunker configuration.
        """
        self.config = config or {}
        self.chunk_size = self.config.get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 200)
    
    def chunk(self, text: str) -> List[str]:
        """Split text into chunks.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of text chunks.
        """
        return [text]


class FixedSizeChunker(Chunker):
    """Fixed-size text chunking with overlap."""
    
    def __init__(self, config: dict = None):
        """Initialize fixed-size chunker.
        
        Args:
            config: Chunker configuration.
        """
        super().__init__(config)
        self.separator = self.config.get("separator", " ")
    
    def chunk(self, text: str) -> List[str]:
        """Split text into fixed-size chunks with overlap.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of text chunks.
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence ending characters near the boundary
                boundary_chars = ['.', '!', '?', '\n']
                best_break = end
                
                for char in boundary_chars:
                    # Search backwards from the boundary
                    for i in range(end - 1, max(start, end - 100), -1):
                        if text[i] == char:
                            best_break = i + 1
                            break
                    if best_break != end:
                        break
                
                end = best_break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - self.chunk_overlap)
        
        return chunks


class RecursiveCharacterChunker(Chunker):
    """Recursive character-based chunking that respects structure."""
    
    def __init__(self, config: dict = None):
        """Initialize recursive character chunker.
        
        Args:
            config: Chunker configuration.
        """
        super().__init__(config)
        self.separators = self.config.get(
            "separators", 
            ["\n\n\n", "\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
    
    def chunk(self, text: str) -> List[str]:
        """Split text recursively using separators.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of text chunks.
        """
        return self._split_text(text, self.separators)
    
    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators.
        
        Args:
            text: Text to split.
            separators: List of separators to try.
            
        Returns:
            List of text chunks.
        """
        # Base case: no more separators or text is small enough
        if not separators or len(text) <= self.chunk_size:
            return [text]
        
        separator = separators[0]
        remaining_seps = separators[1:]
        
        # Split by current separator
        parts = text.split(separator)
        
        # Combine parts that are too small, split parts that are too large
        chunks = []
        current_chunk = ""
        
        for part in parts:
            test_chunk = current_chunk + (separator if current_chunk else "") + part
            
            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    # Current chunk is at size limit, add it
                    chunks.append(current_chunk.strip())
                    current_chunk = part
                else:
                    # Single part is too large, split it recursively
                    sub_chunks = self._split_text(part, remaining_seps)
                    chunks.extend(sub_chunks)
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Apply overlap if needed
        if self.chunk_overlap > 0:
            chunks = self._apply_overlap(chunks)
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap to chunks.
        
        Args:
            chunks: Original chunks.
            
        Returns:
            Chunks with overlap applied.
        """
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped_chunks.append(chunk)
            else:
                # Add overlap from previous chunk
                prev_chunk = chunks[i - 1]
                overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk
                
                # Find a good break point in the overlap
                break_chars = ['.', '!', '?', '\n', ' ']
                best_break = len(overlap_text)
                
                for char in break_chars:
                    for j in range(len(overlap_text) - 1, -1, -1):
                        if overlap_text[j] == char:
                            best_break = j + 1
                            break
                    if best_break != len(overlap_text):
                        break
                
                overlapped_chunk = overlap_text[best_break:] + chunk
                overlapped_chunks.append(overlapped_chunk.strip())
        
        return overlapped_chunks


class SemanticChunker(Chunker):
    """Semantic-aware text chunking using embeddings."""
    
    def __init__(self, config: dict = None):
        """Initialize semantic chunker.
        
        Args:
            config: Chunker configuration.
        """
        super().__init__(config)
        self._embedder = None
        self.similarity_threshold = self.config.get("similarity_threshold", 0.7)
        self.min_chunk_size = self.config.get("min_chunk_size", 100)
        self.max_chunk_size = self.config.get("max_chunk_size", 2000)
    
    def set_embedder(self, embedder) -> None:
        """Set the embedding model.
        
        Args:
            embedder: Embedder instance.
        """
        self._embedder = embedder
    
    def chunk(self, text: str) -> List[str]:
        """Split text into semantically coherent chunks.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of semantic chunks.
        """
        if not self._embedder:
            logger.warning("No embedder set for semantic chunking, falling back to recursive chunking")
            fallback_chunker = RecursiveCharacterChunker(self.config)
            return fallback_chunker.chunk(text)
        
        # Start with sentence-based splitting
        sentences = self._split_into_sentences(text)
        if len(sentences) <= 1:
            return [text]
        
        # Group sentences by semantic similarity
        chunks = []
        current_chunk = []
        current_text = ""
        
        for sentence in sentences:
            test_text = current_text + " " + sentence if current_text else sentence
            
            if len(test_text) <= self.max_chunk_size:
                if not current_chunk:
                    current_chunk = [sentence]
                    current_text = sentence
                else:
                    # Check semantic similarity with chunk start
                    similarity = self._calculate_similarity(sentence, current_chunk[0])
                    
                    if similarity >= self.similarity_threshold:
                        current_chunk.append(sentence)
                        current_text = test_text
                    else:
                        # Start new chunk
                        if current_text:
                            chunks.append(current_text.strip())
                        current_chunk = [sentence]
                        current_text = sentence
            else:
                # Current chunk is too large, finalize it
                if current_text:
                    chunks.append(current_text.strip())
                current_chunk = [sentence]
                current_text = sentence
        
        # Add the last chunk
        if current_text:
            chunks.append(current_text.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences.
        
        Args:
            text: Text to split.
            
        Returns:
            List of sentences.
        """
        # Simple sentence splitting using regex
        # This is a basic implementation; you could use nltk or spacy for better results
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score.
        """
        try:
            import asyncio
            
            # For synchronous calls, we need to run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                similarity = loop.run_until_complete(self._embedder.similarity(text1, text2))
                return similarity
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0


class MarkdownChunker(RecursiveCharacterChunker):
    """Markdown-aware chunker that respects document structure."""
    
    def __init__(self, config: dict = None):
        """Initialize markdown chunker.
        
        Args:
            config: Chunker configuration.
        """
        super().__init__(config)
        self.separators = self.config.get(
            "separators",
            [
                "\n## ", "\n### ", "\n#### ", "\n##### ", "\n###### ",  # Headers
                "\n```\n",  # Code blocks
                "\n\n\n", "\n\n",  # Paragraphs
                "\n",  # Lines
                ". ", "! ", "? ", " ",  # Sentences and words
                ""
            ]
        )
    
    def chunk(self, text: str) -> List[str]:
        """Split markdown text while preserving structure.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of markdown chunks.
        """
        # Pre-process to preserve code blocks
        chunks = self._split_markdown(text)
        
        # Apply size constraints
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                # If chunk is still too large, use recursive splitting
                sub_chunks = super().chunk(chunk)
                final_chunks.extend(sub_chunks)
        
        return [chunk for chunk in final_chunks if chunk.strip()]
    
    def _split_markdown(self, text: str) -> List[str]:
        """Split markdown while preserving code blocks and headers.
        
        Args:
            text: Markdown text.
            
        Returns:
            List of markdown chunks.
        """
        # Extract code blocks
        code_blocks = []
        code_pattern = r'```(?:\w+)?\n.*?\n```'
        matches = list(re.finditer(code_pattern, text, re.DOTALL))
        
        # Replace code blocks with placeholders
        placeholder = "___CODE_BLOCK_PLACEHOLDER___"
        for i, match in enumerate(matches):
            code_blocks.append(match.group(0))
            text = text.replace(match.group(0), f"{placeholder}_{i}", 1)
        
        # Split by markdown structure
        sections = re.split(r'\n(#{1,6}\s+.+)', text)
        
        chunks = []
        current_section = ""
        
        for i, section in enumerate(sections):
            if i % 2 == 1:  # This is a header
                if current_section:
                    # Add code blocks back
                    for j, code in enumerate(code_blocks):
                        current_section = current_section.replace(f"{placeholder}_{j}", code)
                    chunks.append(current_section.strip())
                
                current_section = section
            else:  # This is content
                current_section += section
        
        # Add the last section
        if current_section:
            # Add code blocks back
            for j, code in enumerate(code_blocks):
                current_section = current_section.replace(f"{placeholder}_{j}", code)
            chunks.append(current_section.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]


class SemanticChunker(Chunker):
    """Semantic-aware text chunking."""
    
    def __init__(self, config: dict = None):
        """Initialize the semantic chunker.
        
        Args:
            config: Chunker configuration.
        """
        super().__init__(config)
        self._embedder = None
    
    def chunk(self, text: str) -> list[str]:
        """Split text into semantically coherent chunks.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of semantic chunks.
        """
        return [text]
