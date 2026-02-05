"""
Jobs Services Package.

Re-exports JobService for backward compatibility.
Usage: from app.jobs.services import JobService
"""

from app.jobs.services.job_service import JobService
from app.jobs.services.access_control import JobAccessControl
from app.jobs.services.embedding_manager import EmbeddingManager
from app.jobs.services.jd_manager import JDManager
from app.jobs.services.status_builder import StatusBuilder

__all__ = [
    "JobService",
    "JobAccessControl",
    "EmbeddingManager",
    "JDManager",
    "StatusBuilder",
]
