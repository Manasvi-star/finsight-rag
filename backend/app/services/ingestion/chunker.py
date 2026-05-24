import uuid
from typing import List, Dict, Any, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(
    documents: List[Dict[str, Any]],
    document_id: Optional[str] = None,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> List[Dict[str, Any]]:
    """
    Splits text from documents/pages into smaller chunks.
    Preserves original metadata (page number, source filename) and adds a chunk_id.

    Args:
        documents: A list of dicts from `load_pdf` containing "text" and "metadata".
        document_id: Optional UUID of the ingested document.
        chunk_size: The target character length of each chunk.
        chunk_overlap: The character overlap between adjacent chunks.

    Returns:
        A list of chunk dictionaries:
        [
            {
                "chunk_id": str,
                "document_id": str or None,
                "text": str,
                "metadata": {
                    "page": int,
                    "source": str,
                    "chunk_index": int
                }
            }
        ]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    chunks: List[Dict[str, Any]] = []
    for doc in documents:
        text = doc.get("text", "")
        meta = doc.get("metadata", {})

        split_texts = splitter.split_text(text)
        for idx, split_text in enumerate(split_texts):
            chunk_metadata = meta.copy()
            chunk_metadata["chunk_index"] = idx
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "text": split_text,
                "metadata": chunk_metadata,
            })
    return chunks

