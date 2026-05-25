import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from backend.app.models.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    job_id = Column(String, index=True, nullable=True)
    status = Column(String, default="processing")  # processing, ready, failed
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    page_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
