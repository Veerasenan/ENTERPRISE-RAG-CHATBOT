"""LLM factory — Google Gemini only."""
from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.settings import settings
from app.utils.logger import logger


@lru_cache
def get_chat_llm(streaming: bool = False) -> BaseChatModel:
    print("CHAT MODEL =", settings.GEMINI_CHAT_MODEL)
    logger.info(f"Initializing Gemini chat model: {settings.GEMINI_CHAT_MODEL}")
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_CHAT_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
        streaming=streaming,
    )
