"""Pydantic schemas for document upload/list/delete endpoints."""
from datetime import datetime

from pydantic import BaseModel

from app.models.user import RoleEnum


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    num_chunks: int
    allowed_roles: list[RoleEnum]
    message: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    uploaded_by: str
    allowed_roles: list[str]
    num_chunks: int
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
