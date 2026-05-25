import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FinSight RAG API"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-finsight-rag-development-1234567890")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./finrag.db")

    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # LLM
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    # Directories for persistence
    PERSIST_DIR: str = os.getenv("PERSIST_DIR", "./persist")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./persist/uploads")
    INDEX_DIR: str = os.getenv("INDEX_DIR", "./persist/indices")

    # ML Model Configs
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    SENTIMENT_MODEL_NAME: str = "ProsusAI/finbert"
    SPACY_MODEL_NAME: str = "en_core_web_sm"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.PERSIST_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.INDEX_DIR, exist_ok=True)
