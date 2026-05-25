import json
import os
from typing import List, Dict, Any, Tuple
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.app.core.config import settings

class EmbedderService:
    def __init__(self):
        # Lazy load model when needed to optimize startup time
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return self._model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generates normalized sentence embeddings in batches.
        """
        if not texts:
            return np.empty((0, 0), dtype=np.float32)
        
        # normalize_embeddings=True ensures inner product (IP) functions as cosine similarity
        embeddings = self.model.encode(
            texts, 
            batch_size=64, 
            normalize_embeddings=True, 
            show_progress_bar=False
        )
        return np.array(embeddings, dtype=np.float32)

    def build_and_save_index(self, document_id: str, chunks: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Builds a FAISS FlatIP index, maps it to chunk metadata, and persists to disk.
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embed_texts(texts)
        
        if embeddings.size == 0:
            raise ValueError("No text provided to embed.")

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        # Ensure the index directory exists
        os.makedirs(settings.INDEX_DIR, exist_ok=True)
        index_path = os.path.join(settings.INDEX_DIR, f"{document_id}.faiss")
        meta_path = os.path.join(settings.INDEX_DIR, f"{document_id}.meta.json")

        # Save FAISS index
        faiss.write_index(index, index_path)

        # Save metadata mapping index position to chunk metadata
        # Ensure chunks is serializable
        serialized_chunks = []
        for idx, chunk in enumerate(chunks):
            serialized_chunks.append({
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("document_id"),
                "text": chunk.get("text"),
                "page": chunk.get("metadata", {}).get("page"),
                "source": chunk.get("metadata", {}).get("source"),
                "chunk_index": chunk.get("metadata", {}).get("chunk_index"),
            })

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(serialized_chunks, f, ensure_ascii=False, indent=2)

        return index_path, meta_path

    def load_index(self, document_id: str) -> Tuple[faiss.Index, List[Dict[str, Any]]]:
        """
        Loads the FAISS index and chunk metadata mapping for a document_id.
        """
        index_path = os.path.join(settings.INDEX_DIR, f"{document_id}.faiss")
        meta_path = os.path.join(settings.INDEX_DIR, f"{document_id}.meta.json")

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(f"Index or metadata not found for document {document_id}")

        index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        return index, chunks


embedder_service = EmbedderService()
