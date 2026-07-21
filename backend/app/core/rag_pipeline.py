"""
Core Retrieval-Augmented Generation pipeline — role-aware.
Retrieval is always scoped to the requesting user's visible_roles BEFORE the
LLM ever sees any text, so restricted content can never leak through the model.
"""
from collections import defaultdict
from typing import AsyncGenerator, Dict, List, Tuple

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from app.config.prompts import NO_CONTEXT_MESSAGE, QA_PROMPT_TEMPLATE, SYSTEM_PROMPT
from app.config.settings import settings
from app.core.llm import get_chat_llm
from app.core.vector_store import get_vector_store
from app.utils.logger import logger

# Per-user, per-session in-memory chat history: {"user_id:session_id": [(role, content), ...]}
_CHAT_HISTORY: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
MAX_HISTORY_TURNS = 6


def _format_history(key: str) -> str:
    turns = _CHAT_HISTORY[key][-MAX_HISTORY_TURNS:]
    if not turns:
        return "(no previous conversation)"
    return "\n".join(f"{r.capitalize()}: {c}" for r, c in turns)


def _format_context(docs: List[Document]) -> str:
    if not docs:
        return "(no relevant context found)"
    parts = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("filename", "unknown")
        page = doc.metadata.get("page", "?")
        parts.append(f"[Chunk {i} | source: {source} | page: {page}]\n{doc.page_content}")
    return "\n\n".join(parts)

def _extract_text(content) -> str:
    """
    Normalize LangChain message content into plain text.
    Newer Gemini models sometimes return `content` as a list of content
    blocks (e.g. [{'type': 'text', 'text': '...', 'index': 0}]) instead of a
    plain string. This handles both shapes safely.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(block.get("text", ""))
        return "".join(parts)
    return str(content) if content else ""


class RAGPipeline:
    def __init__(self) -> None:
        self.vector_store = get_vector_store()

    def _retrieve(self, question: str, top_k: int, visible_roles: List[str]) -> List[Document]:
        return self.vector_store.similarity_search(
            query=question, top_k=top_k, visible_roles=visible_roles
        )

    def answer(
        self,
        question: str,
        user_id: str,
        role: str,
        visible_roles: List[str],
        session_id: str,
        top_k: int | None = None,
    ) -> Tuple[str, List[Document]]:
        """Retrieve (role-scoped) context, build prompt, call the LLM, return (answer, sources)."""
        top_k = top_k or settings.TOP_K
        history_key = f"{user_id}:{session_id}"

        docs = self._retrieve(question, top_k, visible_roles)

        if not docs:
            logger.info(f"No accessible documents for role={role}, question={question!r}")
            _CHAT_HISTORY[history_key].append(("user", question))
            _CHAT_HISTORY[history_key].append(("assistant", NO_CONTEXT_MESSAGE))
            return NO_CONTEXT_MESSAGE, []

        prompt = QA_PROMPT_TEMPLATE.format(
            system_prompt=SYSTEM_PROMPT.format(role=role),
            context=_format_context(docs),
            chat_history=_format_history(history_key),
            question=question,
        )

        llm = get_chat_llm(streaming=False)
        response = llm.invoke([HumanMessage(content=prompt)])
        answer_text = _extract_text(response.content)

        _CHAT_HISTORY[history_key].append(("user", question))
        _CHAT_HISTORY[history_key].append(("assistant", answer_text))
        return answer_text, docs

    async def astream_answer(
        self,
        question: str,
        user_id: str,
        role: str,
        visible_roles: List[str],
        session_id: str,
        top_k: int | None = None,
    ) -> AsyncGenerator[str, None]:
        top_k = top_k or settings.TOP_K
        history_key = f"{user_id}:{session_id}"

        docs = self._retrieve(question, top_k, visible_roles)

        if not docs:
            yield NO_CONTEXT_MESSAGE
            _CHAT_HISTORY[history_key].append(("user", question))
            _CHAT_HISTORY[history_key].append(("assistant", NO_CONTEXT_MESSAGE))
            return

        prompt = QA_PROMPT_TEMPLATE.format(
            system_prompt=SYSTEM_PROMPT.format(role=role),
            context=_format_context(docs),
            chat_history=_format_history(history_key),
            question=question,
        )

        llm = get_chat_llm(streaming=True)
        full_answer = ""
        async for chunk in llm.astream([HumanMessage(content=prompt)]):
            token = _extract_text(chunk.content)
            full_answer += token
            if token:
                yield token

        _CHAT_HISTORY[history_key].append(("user", question))
        _CHAT_HISTORY[history_key].append(("assistant", full_answer))

    def clear_history(self, user_id: str, session_id: str) -> None:
        _CHAT_HISTORY.pop(f"{user_id}:{session_id}", None)


def get_rag_pipeline() -> RAGPipeline:
    return RAGPipeline()
