"""
Jobs App Dependencies

FastAPI dependency injection providers for the jobs module.
Centralizes service construction with proper dependency wiring.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.config import get_settings, Settings
from app.jobs.repository import JobRepository
from app.jobs.services import JobService
from app.workflow.engine import WorkflowEngine
from app.ai.embeddings import PineconeService


def get_job_repository(
    session: AsyncSession = Depends(get_db_session),
) -> JobRepository:
    """Provide a JobRepository instance with injected session."""
    return JobRepository(session)


def get_workflow_engine() -> WorkflowEngine:
    """Provide a WorkflowEngine instance."""
    return WorkflowEngine()


def get_pinecone_service() -> PineconeService:
    """Provide a PineconeService instance."""
    return PineconeService()


def get_job_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
    repository: JobRepository = Depends(get_job_repository),
    workflow_engine: WorkflowEngine = Depends(get_workflow_engine),
    pinecone_service: PineconeService = Depends(get_pinecone_service),
) -> JobService:
    """
    Provide a fully-wired JobService instance.

    All dependencies are injected via FastAPI's dependency system,
    making the service fully testable with mock dependencies.
    """
    return JobService(
        session=session,
        settings=settings,
        repository=repository,
        workflow_engine=workflow_engine,
        pinecone_service=pinecone_service,
    )
