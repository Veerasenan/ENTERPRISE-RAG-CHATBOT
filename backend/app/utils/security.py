"""File validation and filename sanitization helpers (not auth security - see core/security.py)."""
import os
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config.settings import settings

ALLOWED_EXTENSIONS = {".pdf"}
FILENAME_SAFE_RE = re.compile(r"[^A-Za-z0-9_.-]")


def sanitize_filename(filename: str) -> str:
    base = os.path.basename(filename)
    base = FILENAME_SAFE_RE.sub("_", base)
    return f"{uuid.uuid4().hex[:8]}_{base}"


def validate_pdf_file(file: UploadFile) -> None:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported file type '{ext}'. Only PDF allowed.")
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid content type. Only PDF files are allowed.")


def validate_file_size(size_bytes: int) -> None:
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File too large. Max allowed is {settings.MAX_FILE_SIZE_MB} MB.",
        )
