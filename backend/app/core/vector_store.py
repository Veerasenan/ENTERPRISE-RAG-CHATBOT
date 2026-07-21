"""
ChromaDB vector store wrapper with ROLE-BASED metadata filtering.
This is the enforcement point: a user's `visible_roles` are passed into every
similarity search, so restricted chunks are never retrieved in the first place.
"""
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config.settings import settings
from app.core.embeddings import get_embeddings
from app.utils.logger import logger


class VectorStoreManager:
    _instance: Optional["VectorStoreManager"] = None

    def __init__(self) -> None:
        self.embeddings = get_embeddings()
        self.store = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR,
        )
        logger.info(f"Chroma collection '{settings.CHROMA_COLLECTION_NAME}' ready")

    @classmethod
    def get_instance(cls) -> "VectorStoreManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Embed and persist chunks. Each chunk's metadata MUST already include
        boolean role flags (role_employee/role_manager/role_hr) set by the
        ingestion service — Chroma metadata values must be scalars (str/int/
        float/bool), so a list like allowed_roles=[...] cannot be filtered with
        $in directly. Booleans per role are the reliable equivalent."""
        ids = self.store.add_documents(documents)
        logger.info(f"Added {len(documents)} chunks to vector store")
        return ids

    def similarity_search(
        self,
        query: str,
        top_k: int,
        visible_roles: List[str],
        document_ids: Optional[List[str]] = None,
    ) -> List[Document]:
        """Role-filtered semantic search. `visible_roles` comes from the
        requesting user (e.g. Manager -> ["Employee","Manager"]). We OR together
        the boolean flag for each visible role — a chunk matches if ANY of its
        role flags for the user's visible roles is True. Chunks tagged only for
        roles outside this list never match, so they're excluded by Chroma
        itself before anything reaches the LLM."""
        role_field_map = {"Employee": "role_employee", "Manager": "role_manager", "HR": "role_hr"}
        role_conditions = [{role_field_map[r]: True} for r in visible_roles if r in role_field_map]
        role_filter = {"$or": role_conditions} if len(role_conditions) > 1 else role_conditions[0]

        if document_ids:
            filter_dict = {"$and": [role_filter, {"document_id": {"$in": document_ids}}]}
        else:
            filter_dict = role_filter

        return self.store.similarity_search(query, k=top_k, filter=filter_dict)

    def delete_document(self, document_id: str) -> None:
        self.store.delete(where={"document_id": document_id})
        logger.info(f"Deleted all chunks for document_id={document_id}")


def get_vector_store() -> VectorStoreManager:
    return VectorStoreManager.get_instance()
