from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.document import Document
from backend.app.models.chunk import Chunk
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user
from backend.app.services.analysis.sentiment import sentiment_service
from backend.app.services.analysis.risk_detector import risk_detector_service
from backend.app.services.analysis.summarizer import summarizer_service

router = APIRouter(prefix="/analysis", tags=["Financial Analysis"])


# Pydantic schemas
class SentimentRequest(BaseModel):
    document_id: str
    section_text: Optional[str] = None


class ChunkScore(BaseModel):
    text: str
    label: str
    score: float


class SentimentResponse(BaseModel):
    label: str
    score: float
    chunk_scores: List[ChunkScore]


class AnalysisRequest(BaseModel):
    document_id: str


class SectionRisk(BaseModel):
    heading: str
    score: float
    flags: List[str]
    excerpt: str


class RiskResponse(BaseModel):
    overall_score: float
    sections: List[SectionRisk]


class SummaryResponse(BaseModel):
    summary: str
    highlights: List[str]
    generated_at: str


@router.post("/sentiment")
def analyze_section_sentiment(
    req: SentimentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes sentiment. If section_text is provided, does section-level FinBERT analysis.
    If section_text is not provided, does document-level page-by-page FinBERT analysis.
    """
    # Verify document ownership for security
    doc = db.query(Document).filter(
        Document.id == req.document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    # 1. Section-level sentiment
    if req.section_text and req.section_text.strip():
        result = sentiment_service.analyze_section(req.section_text)
        return {
            "label": result["label"],
            "score": result["score"],
            "chunk_scores": [
                {"text": c["text"], "label": c["label"], "score": c["score"]}
                for c in result["chunk_scores"]
            ]
        }

    # 2. Document-level sentiment breakdown
    db_chunks = db.query(Chunk).filter(Chunk.document_id == req.document_id).order_by(Chunk.chunk_index).all()
    if not db_chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text chunks found for this document."
        )

    # Group chunks by page number
    page_chunks = {}
    for chunk in db_chunks:
        page_chunks.setdefault(chunk.page_number, []).append(chunk.text)

    sections_sentiment = []
    overall_bullish_count = 0
    overall_neutral_count = 0
    overall_bearish_count = 0
    total_chunks = len(db_chunks)

    for page, texts in sorted(page_chunks.items()):
        combined_text = " ".join(texts)
        res = sentiment_service.analyze_section(combined_text)
        
        page_bullish = sum(1 for c in res["chunk_scores"] if c["label"] == "Bullish")
        page_neutral = sum(1 for c in res["chunk_scores"] if c["label"] == "Neutral")
        page_bearish = sum(1 for c in res["chunk_scores"] if c["label"] == "Bearish")
        page_total = len(res["chunk_scores"]) or 1
        
        overall_bullish_count += page_bullish
        overall_neutral_count += page_neutral
        overall_bearish_count += page_bearish
        
        score_val = (page_bullish - page_bearish) / page_total
        score_str = f"+{score_val:.2f}" if score_val >= 0 else f"{score_val:.2f}"
        
        sections_sentiment.append({
            "name": f"Page {page}",
            "bullish": round((page_bullish / page_total) * 100),
            "neutral": round((page_neutral / page_total) * 100),
            "bearish": round((page_bearish / page_total) * 100),
            "score": score_str
        })

    bullish_pct = round((overall_bullish_count / total_chunks) * 100) if total_chunks else 0
    bearish_pct = round((overall_bearish_count / total_chunks) * 100) if total_chunks else 0
    neutral_pct = 100 - bullish_pct - bearish_pct

    if bullish_pct > bearish_pct + 10:
        overall_label = "bullish"
    elif bearish_pct > bullish_pct + 10:
        overall_label = "bearish"
    else:
        overall_label = "neutral"

    return {
        "overall": overall_label,
        "scores": {
            "bullish": bullish_pct,
            "neutral": neutral_pct,
            "bearish": bearish_pct
        },
        "sections": sections_sentiment
    }


@router.post("/risk", response_model=RiskResponse)
def analyze_document_risk(
    req: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes document risks page-by-page using keyword analysis and spaCy NER.
    """
    doc = db.query(Document).filter(
        Document.id == req.document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    # Fetch document chunks
    db_chunks = db.query(Chunk).filter(Chunk.document_id == req.document_id).order_by(Chunk.chunk_index).all()
    if not db_chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text chunks found for this document. Try re-processing."
        )

    chunks = [
        {
            "text": c.text,
            "page": c.page_number,
            "metadata": {"page": c.page_number}
        }
        for c in db_chunks
    ]

    result = risk_detector_service.analyze_document_risk(chunks)
    return RiskResponse(
        overall_score=result["overall_score"],
        sections=[
            SectionRisk(
                heading=s["heading"],
                score=s["score"],
                flags=s["flags"],
                excerpt=s["excerpt"]
            )
            for s in result["sections"]
        ]
    )


@router.post("/summary", response_model=SummaryResponse)
async def summarize_document(
    req: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Runs a map-reduce summarization chain on the document's pages using Claude.
    """
    doc = db.query(Document).filter(
        Document.id == req.document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    # Fetch document chunks
    db_chunks = db.query(Chunk).filter(Chunk.document_id == req.document_id).order_by(Chunk.chunk_index).all()
    if not db_chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text chunks found for this document."
        )

    chunks = [
        {
            "text": c.text,
            "page": c.page_number,
            "metadata": {"page": c.page_number}
        }
        for c in db_chunks
    ]

    result = await summarizer_service.summarize_document(chunks)
    return SummaryResponse(
        summary=result["summary"],
        highlights=result["highlights"],
        generated_at=result["generated_at"]
    )
