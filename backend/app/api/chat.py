"""
Chat routes — available to ANY logged-in role. Retrieval is always scoped to
current_user.visible_roles, so the role-based restriction happens automatically
on every request, regardless of who's asking.
"""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user
from app.core.rag_pipeline import get_rag_pipeline
from app.models.user import User
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services.retrieval_service import retrieve_sources
from app.utils.logger import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    pipeline = get_rag_pipeline()
    try:
        answer, _ = pipeline.answer(
            question=request.question,
            user_id=current_user.id,
            role=current_user.role.value,
            visible_roles=current_user.visible_roles,
            session_id=request.session_id,
            top_k=request.top_k,
        )
        sources = retrieve_sources(
            query=request.question,
            top_k=request.top_k or 4,
            visible_roles=current_user.visible_roles,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error generating chat response")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))

    return ChatResponse(
        answer=answer, sources=sources, session_id=request.session_id, role=current_user.role.value
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest, current_user: User = Depends(get_current_user)):
    pipeline = get_rag_pipeline()

    async def event_generator():
        try:
            async for token in pipeline.astream_answer(
                question=request.question,
                user_id=current_user.id,
                role=current_user.role.value,
                visible_roles=current_user.visible_roles,
                session_id=request.session_id,
                top_k=request.top_k,
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error during streaming response")
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.delete("/{session_id}/history")
async def clear_history(session_id: str, current_user: User = Depends(get_current_user)) -> dict:
    pipeline = get_rag_pipeline()
    pipeline.clear_history(current_user.id, session_id)
    return {"message": "History cleared."}
