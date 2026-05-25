import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from backend.app.models.database import Base


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
