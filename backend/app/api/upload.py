"""
Document upload routes — restricted to HR. This is where the uploader's
checkbox selection (allowed_roles) is captured and passed into ingestion.
"""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.deps import require_roles
from app.models.user import RoleEnum, User
from app.schemas.document_schemas import DocumentInfo, DocumentListResponse, UploadResponse
from app.services.pdf_processor import delete_document, list_documents, process_and_index_pdf, save_upload
from app.utils.logger import logger

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    allowed_roles: list[RoleEnum] = Form(..., description="Roles that may view this document"),
    current_user: User = Depends(require_roles(RoleEnum.HR.value)),
    db: Session = Depends(get_db),
) -> UploadResponse:
    """Only HR can call this. `allowed_roles` comes from the checkboxes in the
    upload UI (e.g. ["Employee"] or ["Manager","HR"])."""
    try:
        file_path, safe_filename = await save_upload(file)
        record = process_and_index_pdf(
            file_path=file_path,
            original_filename=file.filename or safe_filename,
            allowed_roles=[r.value for r in allowed_roles],
            uploaded_by_user_id=current_user.id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during upload/indexing")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))

    return UploadResponse(
        document_id=record.id,
        filename=record.filename,
        num_chunks=record.num_chunks,
        allowed_roles=[RoleEnum(r) for r in record.allowed_roles],
        message="Document uploaded and indexed successfully.",
    )


@router.get("", response_model=DocumentListResponse)
async def get_documents(
    current_user: User = Depends(require_roles(RoleEnum.HR.value)),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    """Only HR can view the full document registry (who uploaded what, and to which roles)."""
    records = list_documents(db)
    return DocumentListResponse(
        documents=[
            DocumentInfo(
                document_id=r.id,
                filename=r.filename,
                uploaded_by=r.uploaded_by,
                allowed_roles=r.allowed_roles,
                num_chunks=r.num_chunks,
                uploaded_at=r.uploaded_at,
            )
            for r in records
        ]
    )


@router.delete("/{document_id}")
async def remove_document(
    document_id: str,
    current_user: User = Depends(require_roles(RoleEnum.HR.value)),
    db: Session = Depends(get_db),
) -> dict:
    deleted = delete_document(document_id, db)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found.")
    return {"message": f"Document {document_id} deleted successfully."}
