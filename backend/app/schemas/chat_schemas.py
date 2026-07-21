"""Pydantic schemas for chat endpoints."""
from pydantic import BaseModel, Field


class SourceChunk(BaseModel):
    document_id: str
    filename: str
    page: int | None = None
    snippet: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., description="Client-generated conversation id")
    top_k: int | None = Field(default=None, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = []
    session_id: str
    role: str
