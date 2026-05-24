import os
from typing import List, Dict, Any
try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz  # fallback import


def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Load a PDF file and extract text and metadata page‑by‑page.

    Args:
        file_path: Path to the PDF file.

    Returns:
        A list of dictionaries, each representing a page with its text and
        metadata (page number, source filename, total pages).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    doc = fitz.open(file_path)
    total_pages = len(doc)
    pages_data: List[Dict[str, Any]] = []
    source_name = os.path.basename(file_path)

    try:
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text()
            pages_data.append({
                "text": text,
                "metadata": {
                    "page": page_num + 1,
                    "source": source_name,
                    "total_pages": total_pages,
                },
            })
    finally:
        doc.close()

    return pages_data
