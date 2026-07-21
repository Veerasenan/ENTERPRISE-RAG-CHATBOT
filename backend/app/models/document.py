"""
SQLAlchemy ORM model for the document registry (metadata about uploaded PDFs).
The actual vectors/text chunks live in ChromaDB; this table tracks ownership,
role visibility, and lets us list/delete documents cleanly.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    allowed_roles: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    num_chunks: Mapped[int] = mapped_column(Integer, default=0)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Document {self.filename} roles={self.allowed_roles}>"
