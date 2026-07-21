"""Loads PDF files into LangChain Document objects with per-page metadata."""
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from app.utils.logger import logger


def load_pdf(file_path: str, document_id: str, original_filename: str) -> list[Document]:
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    for page in pages:
        page.metadata.update(
            {
                "document_id": document_id,
                "filename": original_filename,
                "page": page.metadata.get("page", 0) + 1,
            }
        )
    logger.info(f"Loaded {len(pages)} pages from '{original_filename}'")
    return pages


def validate_pdf_is_readable(file_path: str) -> bool:
    try:
        loader = PyPDFLoader(file_path)
        return len(loader.load()) > 0
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Failed to read PDF at {file_path}: {exc}")
        return False
