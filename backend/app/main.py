"""FastAPI application entrypoint — Enterprise Role-Based RAG."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import auth, chat, upload
from app.config.database import init_db
from app.config.settings import settings
from app.core.vector_store import get_vector_store
from app.utils.logger import logger

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in '{settings.APP_ENV}' mode")
    init_db()             # create Postgres tables if missing
    get_vector_store()    # warm up Chroma + embeddings
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.APP_NAME,
    description="Role-based Enterprise RAG chatbot (Employee / Manager / HR).",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}")
    return JSONResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, {"detail": "Unexpected server error."})


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(upload.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    return {"status": "ok", "app_name": settings.APP_NAME}


@app.get("/", tags=["System"])
async def root() -> dict:
    return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs"}
