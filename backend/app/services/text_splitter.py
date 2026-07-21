"""Chunking service using RecursiveCharacterTextSplitter."""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import settings
from app.utils.logger import logger


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = get_text_splitter()
    chunks = splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    logger.info(f"Split {len(documents)} pages into {len(chunks)} chunks")
    return chunks
