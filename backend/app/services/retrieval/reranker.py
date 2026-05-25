from typing import List, Dict, Any, Tuple
from sentence_transformers import CrossEncoder
from backend.app.core.config import settings


class RerankerService:
    def __init__(self):
        # Lazy load cross-encoder
        self._model = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            self._model = CrossEncoder(settings.RERANKER_MODEL_NAME)
        return self._model

    def rerank(self, query: str, chunks: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Reranks a list of chunks based on cross-encoder similarity with the query.
        
        Args:
            query: The user query string
            chunks: A list of retrieved chunk dictionaries
            top_n: Number of final chunks to return
            
        Returns:
            A list of top_n chunks sorted by relevance score in descending order.
        """
        if not chunks:
            return []

        # Pairs of (query, document_chunk_text) for scoring
        pairs = [(query, chunk["text"]) for chunk in chunks]
        
        # Compute scores
        scores = self.model.predict(pairs)
        
        # Attach score and sort
        scored_chunks: List[Tuple[float, Dict[str, Any]]] = []
        for idx, score in enumerate(scores):
            chunk_copy = chunks[idx].copy()
            chunk_copy["rerank_score"] = float(score)
            scored_chunks.append((float(score), chunk_copy))
            
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Extract the chunk dictionary for top_n elements
        reranked_chunks = [item[1] for item in scored_chunks[:top_n]]
        return reranked_chunks


reranker_service = RerankerService()
