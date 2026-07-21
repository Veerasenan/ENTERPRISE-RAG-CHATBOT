"""Embeddings factory — Google Gemini only."""
from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config.settings import settings
from app.utils.logger import logger


@lru_cache
def get_embeddings() -> Embeddings:
    logger.info(f"Initializing Gemini embeddings: {settings.GEMINI_EMBEDDING_MODEL}")
    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
    )
