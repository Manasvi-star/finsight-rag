import os
import uuid
import pytest
from backend.app.services.ingestion.embedder import embedder_service
from backend.app.services.retrieval.retriever import retriever_service
from backend.app.services.retrieval.reranker import reranker_service

def test_retrieval_and_reranking_success():
    """
    Verifies that the MMR retriever fetches candidates and the reranker scores them properly.
    """
    document_id = str(uuid.uuid4())
    
    # Create 10 sample chunks with distinct meanings
    chunks = [
        {
            "chunk_id": f"chunk-{i}",
            "document_id": document_id,
            "text": text,
            "metadata": {"page": i + 1, "source": "tcs.pdf", "chunk_index": i}
        }
        for i, text in enumerate([
            "Tata Consultancy Services reports strong revenue growth of 17.6% in 2023.",
            "Operating margin for the fiscal year stood at 24.1%. Net income is healthy.",
            "Banking, Financial Services and Insurance (BFSI) remains the largest vertical.",
            "Cloud migration and generative AI solutions are major growth drivers for us.",
            "Intense competition for digital talent and high attrition are risk factors.",
            "Geopolitical tensions and inflation could impact IT spending patterns.",
            "Cybersecurity threat landscape is evolving rapidly with data privacy concerns.",
            "We are investing in training our workforce on generative AI models.",
            "Dividend payout ratio was maintained at 80% for the shareholders.",
            "Climate change and sustainability goals are integrated into our operations."
        ])
    ]
    
    # Build and save FAISS index
    index_path, meta_path = embedder_service.build_and_save_index(document_id, chunks)
    
    try:
        # 1. Test MMR Retrieval
        # Retrieve 5 chunks out of 10 with MMR
        retrieved = retriever_service.retrieve_chunks(
            document_id=document_id,
            query="Tell me about financial performance and revenue growth.",
            k=8,
            lambda_mult=0.5,
            top_n=5
        )
        
        assert len(retrieved) == 5
        # The first chunk should probably be the revenue one or operating margin one
        assert any("revenue" in chunk["text"].lower() or "margin" in chunk["text"].lower() for chunk in retrieved)
        
        # 2. Test Reranker
        # Rerank the retrieved chunks
        reranked = reranker_service.rerank(
            query="What is the revenue growth rate of TCS in 2023?",
            chunks=retrieved,
            top_n=3
        )
        
        assert len(reranked) == 3
        # Reranker score should be attached
        assert "rerank_score" in reranked[0]
        # The top reranked item should be the one about revenue growth
        assert "revenue growth of 17.6%" in reranked[0]["text"]
        
    finally:
        # Cleanup
        if os.path.exists(index_path):
            os.remove(index_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
