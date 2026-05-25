import os
import uuid
import pytest
import numpy as np
from backend.app.services.ingestion.embedder import embedder_service
from backend.app.core.config import settings

def test_embed_texts_success():
    """
    Verifies that embed_texts generates correct shape of normalized embeddings.
    """
    texts = ["This is a financial document chunk.", "Another chunk containing revenue figures."]
    embeddings = embedder_service.embed_texts(texts)
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] == 384  # bge-small-en-v1.5 dimension is 384
    
    # Verify normalization (magnitude of vectors is ~1)
    for vector in embeddings:
        magnitude = np.linalg.norm(vector)
        assert pytest.approx(magnitude, abs=1e-5) == 1.0

def test_build_save_load_index():
    """
    Verifies that the embedder can build an index of chunks, save it, and load it correctly.
    """
    document_id = str(uuid.uuid4())
    
    # Let's generate 200 chunks to test embedding and indexing scale
    chunks = []
    for i in range(200):
        chunks.append({
            "chunk_id": f"chunk-{i}",
            "document_id": document_id,
            "text": f"This is the text for chunk number {i}. Financial details of Company X in FY23.",
            "metadata": {
                "page": (i // 10) + 1,
                "source": "mock_annual_report.pdf",
                "chunk_index": i % 10
            }
        })
        
    index_path, meta_path = embedder_service.build_and_save_index(document_id, chunks)
    
    assert os.path.exists(index_path)
    assert os.path.exists(meta_path)
    
    # Load index and verify
    index, loaded_chunks = embedder_service.load_index(document_id)
    
    assert index.ntotal == 200
    assert len(loaded_chunks) == 200
    assert loaded_chunks[0]["chunk_id"] == "chunk-0"
    assert loaded_chunks[-1]["chunk_id"] == "chunk-199"
    assert loaded_chunks[50]["page"] == 6
    
    # Cleanup files
    if os.path.exists(index_path):
        os.remove(index_path)
    if os.path.exists(meta_path):
        os.remove(meta_path)
