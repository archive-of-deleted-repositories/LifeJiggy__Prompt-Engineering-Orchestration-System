"""Document summarizer for context compression."""

from typing import List, Dict, Any, Optional
from utilities.token_counter import TokenCounter


class DocumentSummarizer:
    """Summarizes documents for context compression."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the document summarizer.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
        self._token_counter = TokenCounter()
    
    def summarize(
        self,
        document: str,
        max_length: int = 500,
        style: str = "extractive"
    ) -> str:
        """Summarize a document.
        
        Args:
            document: Document text.
            max_length: Maximum summary length.
            style: Summarization style.
            
        Returns:
            Summary text.
        """
        sentences = document.replace("! ", ". ").replace("? ", ". ").split(".")
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return document[:max_length]
        
        word_counts = {}
        for sentence in sentences:
            words = sentence.lower().split()
            for word in words:
                if len(word) > 4:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        sentence_scores = []
        for sentence in sentences:
            words = sentence.lower().split()
            score = sum(word_counts.get(w, 0) for w in words) / max(len(words), 1)
            position_bonus = 1.0 / (sentences.index(sentence) + 1)
            sentence_scores.append((sentence, score * 0.7 + position_bonus * 0.3))
        
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        summary = []
        current_length = 0
        
        for sentence, score in sentence_scores:
            if current_length + len(sentence) <= max_length:
                summary.append(sentence)
                current_length += len(sentence)
        
        return " ".join(summary)
    
    def batch_summarize(
        self,
        documents: List[str],
        max_length: int = 500
    ) -> List[str]:
        """Summarize multiple documents.
        
        Args:
            documents: List of documents.
            max_length: Maximum summary length.
            
        Returns:
            List of summaries.
        """
        return [self.summarize(doc, max_length) for doc in documents]


class ConversationSummarizer:
    """Summarizes conversations for memory."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the conversation summarizer.
        
        Args:
            config: Configuration.
        """
        self.config = config or {}
        self._token_counter = TokenCounter()
    
    def summarize_conversation(
        self,
        messages: List[Dict[str, str]],
        max_length: int = 300
    ) -> str:
        """Summarize a conversation.
        
        Args:
            messages: Conversation messages.
            max_length: Maximum summary length.
            
        Returns:
            Conversation summary.
        """
        user_msgs = [m for m in messages if m.get("role") == "user"]
        assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
        
        topics = []
        for msg in user_msgs:
            content = msg.get("content", "")
            words = content.split()[:5]
            if words:
                topics.append(" ".join(words))
        
        num_exchanges = min(len(user_msgs), len(assistant_msgs))
        
        summary_parts = [
            f"Conversation with {num_exchanges} exchanges.",
            f"User topics: {', '.join(topics[:3])}" if topics else ""
        ]
        
        summary = ". ".join(filter(None, summary_parts))
        
        return summary[:max_length]
    
    def incremental_summary(
        self,
        existing_summary: str,
        new_messages: List[Dict[str, str]]
    ) -> str:
        """Update summary with new messages.
        
        Args:
            existing_summary: Current summary.
            new_messages: New messages to add.
            
        Returns:
            Updated summary.
        """
        if not new_messages:
            return existing_summary
        
        new_summary = self.summarize_conversation(new_messages, max_length=150)
        
        if existing_summary:
            combined = f"{existing_summary} {new_summary}"
            return combined[:300]
        
        return new_summary
