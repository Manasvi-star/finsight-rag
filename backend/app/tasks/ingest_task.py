import logging
from backend.app.tasks.celery_app import celery_app
from backend.app.models.database import SessionLocal
from backend.app.models.document import Document
from backend.app.models.chunk import Chunk
from backend.app.services.ingestion.pdf_loader import load_pdf
from backend.app.services.ingestion.chunker import chunk_documents
from backend.app.services.ingestion.embedder import embedder_service

logger = logging.getLogger("finsight_rag")


def _safe_update_state(task, state: str, meta: dict):
    """Attempts to call task.update_state; silently skips if unavailable."""
    try:
        if task is not None and hasattr(task, "update_state"):
            task.update_state(state=state, meta=meta)
    except Exception:
        pass


def run_ingestion(document_id: str, file_path: str, task=None) -> dict:
    """
    Core ingestion logic, callable both from a Celery task and synchronously.

    1. Extracts text/pages via PyMuPDF.
    2. Splits pages into text chunks.
    3. Generates embeddings and builds a FAISS FlatIP index.
    4. Persists the index to disk and metadata to the database.
    """
    logger.info(f"Starting ingestion for document {document_id}")
    _safe_update_state(task, "PROGRESS", {"progress": 10})

    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found in database.")
        
        assert doc is not None

        doc.status = "processing"  # type: ignore
        db.commit()

        # Step 1: Load PDF pages
        _safe_update_state(task, "PROGRESS", {"progress": 20})
        pages = load_pdf(file_path)
        page_count = len(pages)

        doc.page_count = page_count  # type: ignore
        db.commit()

        # Step 2: Chunk documents
        _safe_update_state(task, "PROGRESS", {"progress": 40})
        chunks = chunk_documents(pages, document_id=document_id)
        chunk_count = len(chunks)

        if chunk_count == 0:
            raise ValueError("No text extracted from PDF, zero chunks generated.")

        # Step 3: Embed and save FAISS index
        _safe_update_state(task, "PROGRESS", {"progress": 60})
        embedder_service.build_and_save_index(document_id, chunks)

        # Step 4: Persist chunks to database
        _safe_update_state(task, "PROGRESS", {"progress": 80})

        db.query(Chunk).filter(Chunk.document_id == document_id).delete()

        db_chunks = [
            Chunk(
                id=c["chunk_id"],
                document_id=document_id,
                text=c["text"],
                page_number=c["metadata"]["page"],
                chunk_index=c["metadata"]["chunk_index"]
            )
            for c in chunks
        ]
        db.bulk_save_objects(db_chunks)

        doc.chunk_count = chunk_count  # type: ignore
        doc.status = "ready"  # type: ignore
        db.commit()

        _safe_update_state(task, "SUCCESS", {"progress": 100})
        logger.info(f"Ingestion completed for document {document_id}")
        return {"status": "ready", "page_count": page_count, "chunk_count": chunk_count}

    except Exception as e:
        logger.error(f"Failed ingestion for document {document_id}: {str(e)}", exc_info=True)
        db.rollback()
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "failed"  # type: ignore
                db.commit()
        except Exception:
            pass
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


@celery_app.task(bind=True, name="backend.app.tasks.ingest_task.ingest_pdf_task")
def ingest_pdf_task(self, document_id: str, file_path: str) -> dict:
    """Celery wrapper around run_ingestion, passing self for state updates."""
    return run_ingestion(document_id, file_path, task=self)
