import os
import pytest
from backend.app.services.ingestion.pdf_loader import load_pdf

def test_load_pdf_success(sample_pdf_path):
    """
    Verifies that load_pdf successfully reads the PDF, extracts correct text,
    and attaches exact metadata parameters (page number, total pages, source).
    """
    pages = load_pdf(sample_pdf_path)
    
    # Verify the results are loaded as a list of pages
    assert isinstance(pages, list)
    assert len(pages) == 3
    
    # Test first page
    page1 = pages[0]
    assert "text" in page1
    assert "metadata" in page1
    assert page1["metadata"]["page"] == 1
    assert page1["metadata"]["total_pages"] == 3
    assert page1["metadata"]["source"] == "tcs_annual_report_2023_sample.pdf"
    assert "Tata Consultancy Services" in page1["text"]
    assert "Revenue reached" in page1["text"]
    
    # Test second page
    page2 = pages[1]
    assert page2["metadata"]["page"] == 2
    assert "BFSI" in page2["text"]
    assert "Digital transformation" in page2["text"]
    
    # Test third page
    page3 = pages[2]
    assert page3["metadata"]["page"] == 3
    assert "Risk Factors" in page3["text"]
    assert "Cybersecurity" in page3["text"]

def test_load_pdf_file_not_found():
    """
    Verifies that load_pdf raises FileNotFoundError when given a non-existent file path.
    """
    with pytest.raises(FileNotFoundError):
        load_pdf("non_existent_annual_report.pdf")
