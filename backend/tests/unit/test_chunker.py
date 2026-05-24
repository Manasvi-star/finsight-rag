import uuid
import pytest
from backend.app.services.ingestion.pdf_loader import load_pdf
from backend.app.services.ingestion.chunker import chunk_documents

def test_chunk_documents_success(sample_pdf_path):
    """
    Verifies that chunk_documents correctly chunks the parsed pages, 
    obeys chunk size limits, generates UUIDs, links document_id, 
    and retains page-level metadata.
    """
    pages = load_pdf(sample_pdf_path)
    
    doc_id = str(uuid.uuid4())
    chunk_size = 80
    chunk_overlap = 15
    
    chunks = chunk_documents(
        pages, 
        document_id=doc_id, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    assert isinstance(chunks, list)
    # Since chunk_size is small, it should split pages into multiple chunks
    assert len(chunks) > len(pages)
    
    # Validate structure and values of each chunk
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert isinstance(chunk["chunk_id"], str)
        assert len(chunk["chunk_id"]) == 36  # UUID length
        
        assert chunk["document_id"] == doc_id
        assert "text" in chunk
        assert len(chunk["text"]) <= chunk_size
        
        # Verify metadata preservation
        meta = chunk["metadata"]
        assert "page" in meta
        assert "source" in meta
        assert "chunk_index" in meta
        assert meta["source"] == "tcs_annual_report_2023_sample.pdf"
        assert meta["total_pages"] == 3
        
    # Verify that chunk_index is sequential for each page
    page_chunk_indices = {}
    for chunk in chunks:
        page = chunk["metadata"]["page"]
        idx = chunk["metadata"]["chunk_index"]
        if page not in page_chunk_indices:
            page_chunk_indices[page] = []
        page_chunk_indices[page].append(idx)
        
    for page, indices in page_chunk_indices.items():
        assert indices == list(range(len(indices)))

def test_chunk_documents_empty():
    """
    Verifies that chunk_documents handles empty input gracefully.
    """
    chunks = chunk_documents([])
    assert chunks == []
