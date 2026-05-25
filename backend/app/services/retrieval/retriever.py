import numpy as np
from typing import List, Dict, Any
from backend.app.services.ingestion.embedder import embedder_service


def maximal_marginal_relevance(
    query_vector: np.ndarray,
    candidate_vectors: np.ndarray,
    lambda_mult: float = 0.5,
    k: int = 5,
) -> List[int]:
    """
    Computes MMR to select a diverse subset of documents from candidates.
    
    Args:
        query_vector: Normalized query embedding of shape (d,)
        candidate_vectors: Normalized candidate embeddings of shape (N, d)
        lambda_mult: Parameter balancing relevance (1.0) and diversity (0.0)
        k: Number of items to select
        
    Returns:
        A list of candidate indices representing the chosen items.
    """
    if len(candidate_vectors) == 0:
        return []
    
    # Candidate vectors shape: (N, d). Query vector shape: (d,)
    # Dot product since vectors are normalized
    relevances = np.dot(candidate_vectors, query_vector)
    
    selected_indices: List[int] = []
    
    for _ in range(min(k, len(candidate_vectors))):
        if not selected_indices:
            best_idx = int(np.argmax(relevances))
            selected_indices.append(best_idx)
        else:
            selected_vectors = candidate_vectors[selected_indices]
            # Dot product shape: (N, S)
            similarities_to_selected = np.dot(candidate_vectors, selected_vectors.T)
            # Max similarity to any selected item: shape (N,)
            max_sim_to_selected = np.max(similarities_to_selected, axis=1)
            
            mmr_scores = lambda_mult * relevances - (1 - lambda_mult) * max_sim_to_selected
            
            # Mask out already selected items
            for idx in selected_indices:
                mmr_scores[idx] = -np.inf
                
            best_idx = int(np.argmax(mmr_scores))
            selected_indices.append(best_idx)
            
    return selected_indices


class RetrieverService:
    def retrieve_chunks(
        self, 
        document_id: str, 
        query: str, 
        k: int = 20, 
        lambda_mult: float = 0.5, 
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_n diverse chunks using MMR from a candidate pool of size k.
        """
        # Load FAISS index and chunk metadata
        index, chunks = embedder_service.load_index(document_id)
        
        # Embed query and normalize
        query_embedding = embedder_service.embed_texts([query])[0]
        
        # Search candidate pool of size k
        # IndexFlatIP search returns cosine similarities (dot product) and integer IDs
        distances, indices = index.search(
            np.array([query_embedding], dtype=np.float32), 
            min(k, len(chunks))
        )
        
        candidate_ids = indices[0]
        
        # Filter invalid index mappings
        valid_indices = [int(i) for i in candidate_ids if i != -1 and i < len(chunks)]
        if not valid_indices:
            return []
            
        # Reconstruct candidate embeddings from FAISS
        candidate_vectors = []
        for idx in valid_indices:
            vector = index.reconstruct(idx)
            candidate_vectors.append(vector)
            
        candidate_vectors_np = np.array(candidate_vectors, dtype=np.float32)
        
        # Apply MMR selection
        selected_cand_indices = maximal_marginal_relevance(
            query_vector=query_embedding,
            candidate_vectors=candidate_vectors_np,
            lambda_mult=lambda_mult,
            k=top_n
        )
        
        # Map selected candidate indices back to chunks
        result_chunks = []
        for cand_idx in selected_cand_indices:
            real_chunk_idx = valid_indices[cand_idx]
            chunk_data = chunks[real_chunk_idx]
            result_chunks.append(chunk_data)
            
        return result_chunks


retriever_service = RetrieverService()
