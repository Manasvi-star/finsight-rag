import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from celery.result import AsyncResult

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models.database import get_db
from backend.app.models.document import Document
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user, limiter
from backend.app.tasks.ingest_task import ingest_pdf_task, run_ingestion
from backend.app.tasks.celery_app import celery_app

router = APIRouter(prefix="/documents", tags=["Documents Ingestion"])


class UploadResponse(BaseModel):
    document_id: str
    job_id: str
    status: str


class DocumentInfo(BaseModel):
    id: str
    filename: str
    status: str
    uploaded_at: str
    page_count: int
    chunk_count: int


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    document_id: str
    progress: int


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Saves the uploaded PDF file and triggers the asynchronous chunking + embedding task.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    document_id = str(uuid.uuid4())
    
    # Save the file to disk
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{document_id}{file_extension}"
    saved_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    
    try:
        with open(saved_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        logger.error(f"Failed to save file for upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file."
        )

    # 1. Create database record
    db_doc = Document(
        id=document_id,
        user_id=current_user.id,
        filename=file.filename,
        status="processing",
        job_id=""  # filled in next
    )
    db.add(db_doc)
    db.commit()

    # 2. Trigger Celery task (with sync fallback when Redis is unavailable)
    try:
        task = ingest_pdf_task.delay(document_id, saved_path)
        job_id = task.id
        db_doc.job_id = job_id
        db.commit()
    except Exception as e:
        logger.error(f"Failed to trigger Celery task: {str(e)}")
        # Fallback: run ingestion synchronously
        logger.info("Running ingestion synchronously as fallback.")
        run_ingestion(document_id, saved_path)
        job_id = f"sync-job-{document_id}"
        db_doc.job_id = job_id
        db.commit()

    return UploadResponse(
        document_id=document_id,
        job_id=job_id,
        status="processing"
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists all documents uploaded by the current authenticated user.
    """
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    
    docs_info = []
    for doc in documents:
        docs_info.append(
            DocumentInfo(
                id=doc.id,
                filename=doc.filename,
                status=doc.status,
                uploaded_at=doc.uploaded_at.isoformat() + "Z",
                page_count=doc.page_count,
                chunk_count=doc.chunk_count
            )
        )
        
    return DocumentListResponse(documents=docs_info)


# Map job ID status route
# Note: we register this directly on the app or prefix it correctly.
# The contract says: GET /jobs/{job_id}/status. We can add a router for it or put it in this router.
# Let's write the route on this router, but strip prefix "/documents" for it if registered elsewhere,
# or we can put it in a separate APIRouter or mount it directly in main.py.
# To keep main.py clean and routes cohesive, let's declare a separate APIRouter for jobs!
# Wait! Let's declare a job APIRouter in this file so we keep it in one file, but export it.
# That is a very clean strategy!
jobs_router = APIRouter(prefix="/jobs", tags=["Jobs Progress"])

@jobs_router.get("/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Returns the Celery job processing status and progress for document ingestion.
    """
    doc = db.query(Document).filter(Document.job_id == job_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found."
        )

    # If the database already shows ready or failed, or it is a fallback sync job, return immediately
    if job_id.startswith("sync-job-") or doc.status in ["ready", "failed"]:
        return JobStatusResponse(
            job_id=job_id,
            status=doc.status,
            document_id=doc.id,
            progress=100 if doc.status == "ready" else 0
        )

    # Try checking Celery, but gracefully fall back if Redis is not running
    try:
        result = AsyncResult(job_id, app=celery_app)
        state = result.state
        
        progress = 0
        status_str = "processing"
        
        if state == "SUCCESS":
            progress = 100
            status_str = "ready"
        elif state == "FAILURE":
            progress = 0
            status_str = "failed"
        elif state == "PROGRESS":
            progress = result.info.get("progress", 0) if isinstance(result.info, dict) else 0
            status_str = "processing"
        elif state in ["STARTED", "RECEIVED", "PENDING"]:
            progress = 0
            status_str = "processing"
        else:
            status_str = doc.status
            progress = 100 if doc.status == "ready" else 0
    except Exception as e:
        logger.warning(f"Could not connect to Celery backend to check job status: {str(e)}. Falling back to DB status.")
        status_str = doc.status
        progress = 100 if doc.status == "ready" else 50  # 50% if processing but Redis down

    return JobStatusResponse(
        job_id=job_id,
        status=status_str,
        document_id=doc.id,
        progress=progress
    )
