"""
High-level PDF ingestion orchestrator with ROLE TAGGING:
save file -> validate -> load -> clean -> chunk -> stamp role flags -> embed -> store.

This is where the uploader's checkbox choice (allowed_roles) is converted into
boolean metadata flags on every chunk, which the vector store later filters on.
"""
import re
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.core.vector_store import get_vector_store
from app.models.document import DocumentRecord
from app.models.user import RoleEnum
from app.services.document_loader import load_pdf, validate_pdf_is_readable
from app.services.text_splitter import split_documents
from app.utils.logger import logger
from app.utils.security import sanitize_filename, validate_file_size, validate_pdf_file

WHITESPACE_RE = re.compile(r"[ \t]+")
MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

ALL_ROLES = [RoleEnum.EMPLOYEE.value, RoleEnum.MANAGER.value, RoleEnum.HR.value]
ROLE_TO_FIELD = {
    RoleEnum.EMPLOYEE.value: "role_employee",
    RoleEnum.MANAGER.value: "role_manager",
    RoleEnum.HR.value: "role_hr",
}


def _clean_text(text: str) -> str:
    text = WHITESPACE_RE.sub(" ", text)
    text = MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


async def save_upload(file: UploadFile) -> tuple[str, str]:
    """Persist the uploaded file to disk and return (file_path, safe_filename)."""
    validate_pdf_file(file)
    contents = await file.read()
    validate_file_size(len(contents))

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(file.filename or "document.pdf")
    file_path = upload_dir / safe_name
    with open(file_path, "wb") as f:
        f.write(contents)

    logger.info(f"Saved upload to {file_path}")
    return str(file_path), safe_name


def process_and_index_pdf(
    file_path: str,
    original_filename: str,
    allowed_roles: list[str],
    uploaded_by_user_id: str,
    db: Session,
) -> DocumentRecord:
    """
    Full role-aware ingestion pipeline:
    1. Validate + load + clean + chunk the PDF
    2. Stamp EVERY chunk with boolean role flags derived from `allowed_roles`
       (the checkboxes the uploader selected)
    3. Embed + store chunks in ChromaDB
    4. Record ownership + role visibility in PostgreSQL for listing/deletion
    """
    if not validate_pdf_is_readable(file_path):
        raise ValueError("Uploaded PDF could not be read or contains no extractable text.")

    invalid_roles = set(allowed_roles) - set(ALL_ROLES)
    if invalid_roles:
        raise ValueError(f"Invalid roles specified: {invalid_roles}")
    if not allowed_roles:
        raise ValueError("At least one role must be selected for document visibility.")

    document_id = str(uuid.uuid4())
    pages = load_pdf(file_path, document_id=document_id, original_filename=original_filename)
    for page in pages:
        page.page_content = _clean_text(page.page_content)

    chunks = split_documents(pages)

    # Stamp role visibility as boolean flags (Chroma metadata must be scalar).
    for chunk in chunks:
        for role_name, field in ROLE_TO_FIELD.items():
            chunk.metadata[field] = role_name in allowed_roles

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    record = DocumentRecord(
        id=document_id,
        filename=original_filename,
        file_path=file_path,
        uploaded_by=uploaded_by_user_id,
        allowed_roles=allowed_roles,
        num_chunks=len(chunks),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    logger.info(
        f"Indexed '{original_filename}' as {document_id} "
        f"({len(chunks)} chunks, roles={allowed_roles})"
    )
    return record


def list_documents(db: Session) -> list[DocumentRecord]:
    return db.query(DocumentRecord).order_by(DocumentRecord.uploaded_at.desc()).all()


def delete_document(document_id: str, db: Session) -> bool:
    record = db.get(DocumentRecord, document_id)
    if record is None:
        return False

    vector_store = get_vector_store()
    vector_store.delete_document(document_id)

    file_path = Path(record.file_path)
    if file_path.exists():
        file_path.unlink()

    db.delete(record)
    db.commit()
    logger.info(f"Deleted document {document_id}")
    return True
