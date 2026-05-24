import os
import pytest
try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz  # fallback for newer pymupdf versions

@pytest.fixture(scope="session")
def sample_pdf_path(tmp_path_factory):
    """
    Generates a sample PDF file with structured text across multiple pages
    to test the PDF loader and chunker services.
    """
    temp_dir = tmp_path_factory.mktemp("data")
    pdf_path = str(temp_dir / "tcs_annual_report_2023_sample.pdf")
    
    doc = fitz.open()
    
    # Page 1 text
    page1 = doc.new_page()
    page1.insert_text(
        (50, 50), 
        "Tata Consultancy Services Annual Report 2023.\n"
        "Financial Highlights:\n"
        "Revenue reached 2,25,458 crore INR, showing a growth of 17.6% YoY.\n"
        "Operating Margin stood at 24.1%. Net Income was 42,147 crore INR."
    )
    
    # Page 2 text
    page2 = doc.new_page()
    page2.insert_text(
        (50, 50),
        "Business Segment Performance:\n"
        "Banking, Financial Services and Insurance (BFSI) continues to be the largest vertical.\n"
        "Digital transformation services saw strong demand across all markets.\n"
        "Cloud adoption and generative AI solutions are key growth drivers."
    )
    
    # Page 3 text
    page3 = doc.new_page()
    page3.insert_text(
        (50, 50),
        "Risk Factors:\n"
        "1. Geopolitical tensions and macroeconomic uncertainties could impact client spending.\n"
        "2. Intense competition for talent in key technology areas.\n"
        "3. Cybersecurity and data privacy risks."
    )
    
    doc.save(pdf_path)
    doc.close()
    
    yield pdf_path
