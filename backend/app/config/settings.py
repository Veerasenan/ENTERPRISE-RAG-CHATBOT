"""
Centralized application configuration, loaded from environment variables / .env.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- PostgreSQL ---
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/enterprise_rag_db"

    # --- JWT ---
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    # --- LLM Provider: Google Gemini only ---
    GOOGLE_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"

    # --- App ---
    APP_NAME: str = "Enterprise RAG Chatbot"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- Storage ---
    UPLOAD_DIR: str = "./data/uploaded_pdfs"
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "company_policies"

    # --- Chunking / Retrieval ---
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 4
    MAX_FILE_SIZE_MB: int = 25

    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
