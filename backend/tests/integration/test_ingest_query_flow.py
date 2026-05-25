# Set environment variable before importing main app/database to override setting
import os
os.environ["DATABASE_URL"] = "sqlite:///./test_finrag.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.models import Base, User, Document, Chunk, QueryHistory
from backend.app.models.database import get_db, engine as db_engine
from backend.app.api.dependencies import limiter
from backend.app.tasks.celery_app import celery_app

# Configure Celery to run synchronously in tests
celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)

# Setup test database engine matching the overridden URL
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

# Disable slowapi rate limiting for testing to avoid 429 responses
limiter.enabled = False


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """
    Initializes database tables before each test and drops them after.
    """
    Base.metadata.create_all(bind=db_engine)
    yield
    Base.metadata.drop_all(bind=db_engine)
    
    # Clean up test database file
    try:
        if os.path.exists("./test_finrag.db"):
            os.remove("./test_finrag.db")
    except Exception:
        pass


def test_end_to_end_flow(sample_pdf_path):
    """
    Integration test checking the entire backend pipeline:
    User registration -> Login -> PDF Upload -> Job status check -> Documents list -> RAG Query (SSE) -> Sentiment/Risk/Summary Analysis.
    """
    # 1. Register User
    reg_payload = {"email": "testuser@finsight.com", "password": "securepassword123"}
    reg_response = client.post("/auth/register", json=reg_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert "user_id" in reg_data
    assert reg_data["email"] == "testuser@finsight.com"

    # 2. Login User
    login_response = client.post("/auth/login", json=reg_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Upload Document
    with open(sample_pdf_path, "rb") as f:
        upload_response = client.post(
            "/documents/upload",
            files={"file": ("tcs_report.pdf", f, "application/pdf")},
            headers=headers
        )
        
    assert upload_response.status_code == 202
    upload_data = upload_response.json()
    assert "document_id" in upload_data
    assert "job_id" in upload_data
    assert upload_data["status"] == "processing"
    
    document_id = upload_data["document_id"]
    job_id = upload_data["job_id"]

    # 4. Check Job Status
    status_response = client.get(f"/jobs/{job_id}/status", headers=headers)
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["job_id"] == job_id
    # Since Celery runs synchronously (fallback or eager), status should be ready
    assert status_data["status"] == "ready"
    assert status_data["progress"] == 100
    assert status_data["document_id"] == document_id

    # 5. List Documents
    docs_response = client.get("/documents", headers=headers)
    assert docs_response.status_code == 200
    docs_data = docs_response.json()
    assert "documents" in docs_data
    assert len(docs_data["documents"]) == 1
    doc_info = docs_data["documents"][0]
    assert doc_info["id"] == document_id
    assert doc_info["status"] == "ready"
    assert doc_info["page_count"] == 3
    assert doc_info["chunk_count"] > 0

    # 6. RAG Query via SSE
    query_payload = {
        "document_id": document_id,
        "question": "What is the revenue of TCS in 2023?",
        "history": []
    }
    
    # We use client.stream since the endpoint returns an SSE stream
    with client.stream("POST", "/query", json=query_payload, headers=headers) as stream_response:
        assert stream_response.status_code == 200
        # Read the lines from streamed response
        lines = [line for line in stream_response.iter_lines() if line]
        assert len(lines) > 0
        
        # Verify that we receive SSE data structures
        assert any(line.startswith("data: ") for line in lines)
        
        # The final event should contain answer, sources, and sentiment
        last_event = lines[-1]
        assert "answer" in last_event
        assert "sources" in last_event
        assert "sentiment" in last_event

    # 7. Sentiment Analysis endpoint
    sent_payload = {
        "document_id": document_id,
        "section_text": "TCS reports strong revenues and high net income, but geopolitical margins look volatile."
    }
    sent_response = client.post("/analysis/sentiment", json=sent_payload, headers=headers)
    assert sent_response.status_code == 200
    sent_data = sent_response.json()
    assert "label" in sent_data
    assert "score" in sent_data
    assert "chunk_scores" in sent_data

    # 8. Risk Analysis endpoint
    risk_payload = {"document_id": document_id}
    risk_response = client.post("/analysis/risk", json=risk_payload, headers=headers)
    assert risk_response.status_code == 200
    risk_data = risk_response.json()
    assert "overall_score" in risk_data
    assert "sections" in risk_data
    assert len(risk_data["sections"]) == 3  # The sample report has 3 pages

    # 9. Summary Analysis endpoint
    summary_payload = {"document_id": document_id}
    summary_response = client.post("/analysis/summary", json=summary_payload, headers=headers)
    assert summary_response.status_code == 200
    summary_data = summary_response.json()
    assert "summary" in summary_data
    assert "highlights" in summary_data
    assert "generated_at" in summary_data
    assert len(summary_data["highlights"]) > 0
