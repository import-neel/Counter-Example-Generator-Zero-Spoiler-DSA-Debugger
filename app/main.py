from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_problems import router as problems_router
from app.api.routes_submissions import router as submissions_router
from app.config import settings
from app.database import init_db
from app.services.sandbox_manager import sandbox_manager
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event handler for startup and shutdown."""
    logger.info("Initializing Counter-Example Generator Backend...")
    # Initialize database tables
    init_db()
    logger.info("Database initialized with schema tables.")

    docker_status = "available" if sandbox_manager.is_docker_available else "unavailable (using secure subprocess sandbox)"
    logger.info("Sandbox status: Docker is %s", docker_status)

    yield

    logger.info("Shutting down Counter-Example Generator Backend...")


app = FastAPI(
    title="Counter-Example Generator & Zero-Spoiler DSA Debugger API",
    description="Backend execution engine, security sandboxing, and submission telemetry service.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for Teammate 3 (Streamlit / Frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(submissions_router)
app.include_router(problems_router)


@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health_check() -> Dict[str, str]:
    """Health check endpoint to verify backend status and sandbox engine capability."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "sandbox_mode": settings.SANDBOX_MODE,
        "docker_available": str(sandbox_manager.is_docker_available),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
