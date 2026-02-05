"""
Job access control service.

Handles authorization logic for job operations.
"""

from uuid import UUID

from app.core.exceptions import RecordNotFoundError, ForbiddenError
from app.auth.models import User
from app.jobs.models import JobRecord
from app.jobs.repository import JobRepository


class JobAccessControl:
    """
    Handles job access authorization logic.

    Single Responsibility: Verify user permissions for job operations.
    """

    def __init__(self, repository: JobRepository, logger):
        self.repository = repository
        self.logger = logger

    async def ensure_access(self, job_id: str, user: User) -> JobRecord:
        """
        Verify that the job exists and user has access.

        Global admins (superusers) can access any job.
        Regular users can only access their own jobs.

        Args:
            job_id: Job identifier
            user: Current authenticated user

        Returns:
            JobRecord if access is granted

        Raises:
            RecordNotFoundError: If job doesn't exist
            ForbiddenError: If user lacks permission
        """
        job = await self.repository.get_by_id(UUID(job_id))
        if not job:
            raise RecordNotFoundError("Job", job_id)

        if not user.is_superuser and job.owner_id != user.id:
            self.logger.warning(
                "Unauthorized access attempt",
                extra={
                    "user_id": str(user.id),
                    "job_id": job_id,
                    "action": "access_denied",
                },
            )
            raise ForbiddenError(resource=f"Job {job_id}", user_id=user.id)

        return job
