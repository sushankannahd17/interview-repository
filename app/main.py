from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import async_engine
from app.exceptions.handlers import register_exception_handlers
from app.routers import alumni, companies, integrations, interviews, progress, questions, study_plans
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    yield
    await async_engine.dispose()


app = FastAPI(
    title="Interview & Study Management Platform",
    description="Team A Backend — Data persistence and retrieval APIs",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(integrations.router, prefix="/api/v1")
app.include_router(interviews.router, prefix="/api/v1")
app.include_router(questions.router, prefix="/api/v1")
app.include_router(study_plans.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
app.include_router(companies.router, prefix="/api/v1")
app.include_router(alumni.router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "environment": settings.ENVIRONMENT}
