"""Formats raw vector-store hits into API-friendly source citations."""
from app.core.vector_store import get_vector_store
from app.schemas.chat_schemas import SourceChunk


def retrieve_sources(query: str, top_k: int, visible_roles: list[str]) -> list[SourceChunk]:
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(query=query, top_k=top_k, visible_roles=visible_roles)
    return [
        SourceChunk(
            document_id=doc.metadata.get("document_id", "unknown"),
            filename=doc.metadata.get("filename", "unknown"),
            page=doc.metadata.get("page"),
            snippet=doc.page_content[:300],
        )
        for doc in docs
    ]
