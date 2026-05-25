from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.document import Document
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user, limiter
from backend.app.services.retrieval.retriever import retriever_service
from backend.app.services.retrieval.reranker import reranker_service
from backend.app.services.generation.chain import generate_rag_stream

router = APIRouter(tags=["Query RAG"])


class QueryRequest(BaseModel):
    document_id: str
    question: str
    history: Optional[List[Dict[str, Any]]] = []


@router.post("/query")
@limiter.limit("20/minute")
async def query_document(
    request: Request,
    req: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    RAG Query endpoint:
    1. MMR Retrieval of 20 candidate chunks.
    2. Rerank to top 5 using Cross-Encoder.
    3. Stream answer tokens using SSE.
    4. Yield final event with consolidated answer, sources, and FinBERT sentiment.
    """
    # 1. Verify document exists and belongs to the user or is accessible
    # (Checking ownership ensures security isolation between users!)
    doc = db.query(Document).filter(
        Document.id == req.document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
        
    if doc.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not ready. Current status: {doc.status}"
        )

    # 2. Retrieve chunks (k=20 candidate pool)
    try:
        retrieved_chunks = retriever_service.retrieve_chunks(
            document_id=req.document_id,
            query=req.question,
            k=20,
            lambda_mult=0.5,
            top_n=20  # fetch 20 candidates for reranker stage
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)}"
        )

    # 3. Rerank down to top 5
    try:
        reranked_chunks = reranker_service.rerank(
            query=req.question,
            chunks=retrieved_chunks,
            top_n=5
        )
    except Exception as e:
        # Fallback to MMR results if reranker fails
        reranked_chunks = retrieved_chunks[:5]

    # 4. Stream response via SSE
    generator = generate_rag_stream(
        question=req.question,
        chunks=reranked_chunks,
        history=req.history
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
