"""Keyword-based retriever using BM25."""

import re
import math
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
import logging

logger = logging.getLogger(__name__)


class BM25Retriever:
    """BM25 keyword-based retriever with proper implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize BM25 retriever.
        
        Args:
            config: Retriever configuration.
        """
        self.config = config or {}
        self.k1 = self.config.get("k1", 1.2)
        self.b = self.config.get("b", 0.75)
        self.epsilon = self.config.get("epsilon", 0.25)
        
        self._documents = []
        self._doc_freqs = []
        self._idf = {}
        self._doc_len = []
        self._avg_doc_len = 0
        self._corpus_size = 0
        self._initialized = False
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to BM25 corpus.
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'.
        """
        self._documents = documents
        self._corpus_size = len(documents)
        
        # Preprocess documents
        self._doc_freqs = []
        self._doc_len = []
        
        for doc in documents:
            content = doc.get("content", "")
            tokens = self._tokenize(content)
            
            # Count term frequencies
            term_freqs = Counter(tokens)
            self._doc_freqs.append(term_freqs)
            self._doc_len.append(len(tokens))
        
        # Calculate average document length
        if self._doc_len:
            self._avg_doc_len = sum(self._doc_len) / len(self._doc_len)
        
        # Calculate IDF scores
        self._calculate_idf()
        self._initialized = True
        
        logger.info(f"BM25 retriever initialized with {self._corpus_size} documents")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms.
        
        Args:
            text: Input text.
            
        Returns:
            List of tokens.
        """
        # Simple tokenization - you could use more sophisticated tokenizers
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        tokens = text.split()
        
        # Optional: remove very short tokens and common stop words
        min_token_len = self.config.get("min_token_len", 2)
        tokens = [token for token in tokens if len(token) >= min_token_len]
        
        return tokens
    
    def _calculate_idf(self) -> None:
        """Calculate inverse document frequency scores."""
        # Count document frequency for each term
        df = defaultdict(int)
        for doc_freqs in self._doc_freqs:
            for term in doc_freqs:
                df[term] += 1
        
        # Calculate IDF
        for term, freq in df.items():
            idf = math.log((self._corpus_size - freq + 0.5) / (freq + 0.5))
            self._idf[term] = max(idf, self.epsilon)
    
    async def retrieve(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform BM25 retrieval.
        
        Args:
            query: Query string.
            query_embedding: Not used for BM25.
            top_k: Number of results.
            filters: Metadata filters.
            
        Returns:
            List of search results with BM25 scores.
        """
        if not self._initialized:
            logger.warning("BM25 retriever not initialized with documents")
            return []
        
        # Apply filters
        candidates = self._documents
        if filters:
            candidates = [
                doc for doc in self._documents
                if all(doc.get("metadata", {}).get(k) == v for k, v in filters.items())
            ]
        
        if not candidates:
            return []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        # Calculate BM25 scores
        scores = []
        for i, doc in enumerate(self._documents):
            if doc not in candidates:
                continue
            
            score = self._calculate_bm25_score(query_tokens, i)
            scores.append((score, i, doc))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Return top_k results
        results = []
        for score, doc_idx, doc in scores[:top_k]:
            results.append({
                "id": doc.get("id", f"doc_{doc_idx}"),
                "content": doc.get("content", ""),
                "score": float(score),
                "metadata": doc.get("metadata", {}),
                "retriever": "bm25"
            })
        
        return results
    
    def _calculate_bm25_score(self, query_tokens: List[str], doc_idx: int) -> float:
        """Calculate BM25 score for query-document pair.
        
        Args:
            query_tokens: Tokenized query.
            doc_idx: Document index.
            
        Returns:
            BM25 score.
        """
        score = 0.0
        doc_len = self._doc_len[doc_idx]
        doc_freqs = self._doc_freqs[doc_idx]
        
        for term in query_tokens:
            if term in doc_freqs:
                tf = doc_freqs[term]
                idf = self._idf.get(term, self.epsilon)
                
                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self._avg_doc_len))
                
                score += idf * (numerator / denominator)
        
        return score


class KeywordRetriever:
    """Simplified keyword-based retrieval using BM25-like scoring."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize keyword retriever.
        
        Args:
            config: Retriever configuration.
        """
        self.config = config or {}
        self._documents = {}
        self._index = {}
        self._initialized = False
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to index.
        
        Args:
            documents: List of documents with id, content, metadata.
        """
        for doc in documents:
            doc_id = doc.get("id")
            content = doc.get("content", "")
            self._documents[doc_id] = doc
            self._index[doc_id] = self._tokenize(content)
        
        self._initialized = True
        logger.info(f"Keyword retriever initialized with {len(documents)} documents")
    
    def _tokenize(self, text: str) -> Counter:
        """Tokenize text into words.
        
        Args:
            text: Input text.
            
        Returns:
            Counter of tokens.
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return Counter(tokens)
    
    def _calculate_bm25_score(
        self,
        query_tokens: Counter,
        doc_tokens: Counter,
        doc_length: int,
        avg_doc_length: float,
        k1: float = 1.5,
        b: float = 0.75
    ) -> float:
        """Calculate BM25 score.
        
        Args:
            query_tokens: Query token counts.
            doc_tokens: Document token counts.
            doc_length: Document length.
            avg_doc_length: Average document length.
            k1: BM25 parameter.
            b: BM25 parameter.
            
        Returns:
            BM25 score.
        """
        score = 0.0
        
        for term, tf in query_tokens.items():
            doc_tf = doc_tokens.get(term, 0)
            if doc_tf == 0:
                continue
            
            # Calculate IDF
            df = sum(1 for doc_idx in self._index.values() if term in doc_idx)
            idf = math.log((len(self._documents) - df + 0.5) / (df + 0.5))
            
            # BM25 formula
            numerator = doc_tf * (k1 + 1)
            denominator = doc_tf + k1 * (1 - b + b * doc_length / avg_doc_length)
            
            score += idf * (numerator / denominator)
        
        return score
    
    async def retrieve(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform keyword search.
        
        Args:
            query: Query string.
            query_embedding: Not used for keyword retrieval.
            top_k: Number of results.
            filters: Metadata filters.
            
        Returns:
            List of search results.
        """
        if not self._initialized:
            logger.warning("Keyword retriever not initialized")
            return []
        
        query_tokens = self._tokenize(query)
        
        doc_lengths = {doc_id: sum(tokens.values()) 
                      for doc_id, tokens in self._index.items()}
        avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths) if doc_lengths else 0
        
        scores = []
        for doc_id, doc_tokens in self._index.items():
            doc = self._documents[doc_id]
            
            if filters:
                skip = False
                for key, value in filters.items():
                    if doc.get("metadata", {}).get(key) != value:
                        skip = True
                        break
                if skip:
                    continue
            
            score = self._calculate_bm25_score(
                query_tokens,
                doc_tokens,
                doc_lengths[doc_id],
                avg_doc_length
            )
            scores.append((doc_id, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                "id": doc_id,
                "content": self._documents[doc_id].get("content", ""),
                "score": min(score / max(1, len(query_tokens)), 1.0),
                "metadata": self._documents[doc_id].get("metadata", {}),
                "retriever": "keyword"
            }
            for doc_id, score in scores[:top_k]
        ]
