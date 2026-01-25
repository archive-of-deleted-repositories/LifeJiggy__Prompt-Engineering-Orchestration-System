"""Text splitting utilities."""


class TextSplitter:
    """Splits text into chunks."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """Initialize the text splitter.
        
        Args:
            chunk_size: Maximum chunk size.
            overlap: Overlap between chunks.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split(self, text: str) -> list[str]:
        """Split text into chunks.
        
        Args:
            text: Text to split.
            
        Returns:
            List of text chunks.
        """
        if len(text) <= self.chunk_size:
            return [text]
        return []
    
    def split_by_sentence(self, text: str) -> list[str]:
        """Split text by sentences.
        
        Args:
            text: Text to split.
            
        Returns:
            List of sentence chunks.
        """
        return []
    
    def split_by_paragraph(self, text: str) -> list[str]:
        """Split text by paragraphs.
        
        Args:
            text: Text to split.
            
        Returns:
            List of paragraph chunks.
        """
        return text.split("\n\n")
