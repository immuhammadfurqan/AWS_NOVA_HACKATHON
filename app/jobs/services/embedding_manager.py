"""
Embedding manager service.

Handles job description embeddings in Pinecone.
"""

from datetime import datetime, timezone

from app.jobs.schemas import GeneratedJD
from app.jobs.exceptions import EmbeddingOperationError
from app.ai.embeddings import PineconeService, generate_jd_embedding


class EmbeddingManager:
    """
    Manages job description embeddings in Pinecone.

    Single Responsibility: Handle all embedding operations.
    """

    def __init__(self, pinecone_service: PineconeService, logger):
        self.pinecone_service = pinecone_service
        self.logger = logger

    async def store_jd_embedding(self, job_id: str, jd: GeneratedJD) -> None:
        """
        Generate and store job description embedding.

        Args:
            job_id: Job identifier
            jd: Generated job description

        Raises:
            EmbeddingOperationError: If embedding operation fails
        """
        try:
            embedding = await generate_jd_embedding(jd)
            metadata = self._create_jd_metadata(job_id, jd)
            await self.pinecone_service.upsert_job_embedding(
                job_id, embedding, metadata
            )
        except Exception as e:
            raise EmbeddingOperationError(
                operation="store", job_id=job_id, original_error=str(e)
            )

    async def delete_job_embeddings(self, job_id: str) -> None:
        """
        Delete all embeddings for a job.

        Args:
            job_id: Job identifier

        Note:
            Logs warnings on failure but doesn't raise to allow job deletion to proceed.
        """
        try:
            await self.pinecone_service.delete_job_embeddings(job_id)
        except Exception as e:
            self.logger.warning(
                "Failed to delete embeddings",
                extra={
                    "job_id": job_id,
                    "error": str(e),
                    "retry_needed": True,
                },
            )

    def _create_jd_metadata(self, job_id: str, jd: GeneratedJD) -> dict:
        """Create metadata dict for Pinecone storage."""
        return {
            "job_id": str(job_id),
            "type": "job_description",
            "role_title": jd.job_title,
            "location": jd.location or "Remote",
            "salary_range": jd.salary_range or "Not specified",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
