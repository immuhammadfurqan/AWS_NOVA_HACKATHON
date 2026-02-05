"""
AARLP FastAPI Application

Main API endpoints for the AI-Agentic Recruitment Lifecycle Platform.

This module follows clean architecture principles:
- Modular routes (Django-style apps)
- Dependency injection
- Centralized error handling
- Structured logging
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_database, close_database
from app.core.logging import (
    setup_logging,
    get_logger,
    correlation_id_var,
)
from app.core.exceptions import (
    AARLPException,
    RecordNotFoundError,
    ValidationError,
    ForbiddenError,
)
from app.workflow.exceptions import InvalidStateTransitionError

# Import Routers
from app.jobs.router import router as jobs_router
from app.careers.router import router as careers_router
from app.candidates.router import router as candidates_router
from app.interviews.router import router as interviews_router
from app.auth.router import router as auth_router
from app.users.router import router as users_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    setup_logging()
    logger.info("Starting AARLP application...")

    await init_database()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down AARLP application...")

    # Close Redis connection
    try:
        from app.core.locking import close_redis

        await close_redis()
    except Exception as e:
        logger.warning(f"Error closing Redis: {e}")

    await close_database()
    logger.info("Shutdown complete")


settings = get_settings()

app = FastAPI(
    title="AARLP - AI-Agentic Recruitment Lifecycle Platform",
    description=(
        "Automated JD-to-Interview recruitment pipeline using "
        "LangGraph, CrewAI, and Voice AI"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# Middleware
# ============================================================================

# CORS Configuration - Use environment-based origins for security
origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to each request for tracing."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
    correlation_id_var.set(correlation_id)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id

    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log request/response details."""
    import time

    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = (time.perf_counter() - start_time) * 1000

    logger.info(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code} ({process_time:.2f}ms)"
    )

    return response


# ============================================================================
# Exception Handlers
# ============================================================================


@app.exception_handler(AARLPException)
async def aarlp_exception_handler(request: Request, exc: AARLPException):
    """Handle custom AARLP exceptions."""
    logger.error(f"AARLP Exception: {exc.error_code} - {exc.message}")

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, RecordNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, InvalidStateTransitionError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, ForbiddenError):
        status_code = status.HTTP_403_FORBIDDEN

    return JSONResponse(
        status_code=status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {"correlation_id": correlation_id_var.get()},
        },
    )


# ============================================================================
# Routers
# ============================================================================

# Mount routers
app.include_router(jobs_router)
app.include_router(careers_router)  # Public careers endpoints (no auth)
# Candidates router handles /jobs/{id}/... paths, so we mount at root or check prefix usage
# In app/candidates/views.py, paths are "/jobs/{job_id}/..."
# So if we mount at root, it works.
app.include_router(candidates_router)
app.include_router(interviews_router, prefix="/interviews")
app.include_router(auth_router)
app.include_router(users_router)


# ============================================================================
# Health Check
# ============================================================================


@app.get("/", tags=["Health"])
async def root():
    """Root health check endpoint."""
    return {
        "status": "healthy",
        "service": "AARLP",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Comprehensive health check for load balancers.

    Returns 200 only if all critical dependencies are healthy.
    Returns 503 (Service Unavailable) if any dependency fails.
    """
    from sqlalchemy import text

    checks = {
        "api": "ok",
        "database": "unknown",
    }

    overall_healthy = True

    # Check Database connectivity
    try:
        from app.core.database import get_session_factory

        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
            checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:100]}"
        overall_healthy = False

    return JSONResponse(
        status_code=(
            status.HTTP_200_OK
            if overall_healthy
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content={
            "status": "healthy" if overall_healthy else "unhealthy",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.get("/health/readiness", tags=["Health"])
async def readiness():
    """
    Readiness check for Kubernetes/load balancers.

    Indicates if the service can accept traffic.
    Lighter than full health check - just DB connectivity.
    """
    from sqlalchemy import text

    try:
        from app.core.database import get_session_factory

        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "error": str(e)[:100]},
        )


@app.get("/health/liveness", tags=["Health"])
async def liveness():
    """
    Liveness check for Kubernetes.

    Indicates if the container should be restarted.
    Always returns 200 unless the app is completely broken.
    """
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
