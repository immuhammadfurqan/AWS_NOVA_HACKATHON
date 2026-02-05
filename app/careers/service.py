"""
Careers Service

Business logic for public career pages.
"""

from uuid import UUID

from app.careers.repository import CareersRepository
from app.careers.jsonld_generator import generate_job_posting_jsonld
from app.jobs.schemas import GeneratedJD
from app.jobs.models import JobRecord
from app.core.logging import get_logger

logger = get_logger(__name__)


class CareersService:
    """Service layer for public careers operations."""

    def __init__(self, repository: CareersRepository):
        self.repository = repository

    async def list_public_jobs(self) -> tuple[list[dict], int]:
        """
        Get all approved jobs for public listing.

        Returns:
            Tuple of (job_list, total_count)
        """
        jobs = await self.repository.get_approved_jobs()

        job_items = []
        for job in jobs:
            if job.generated_jd:
                jd = GeneratedJD.model_validate(job.generated_jd)
                job_items.append(
                    {
                        "job_id": job.id,
                        "job_title": jd.job_title,
                        "company_name": job.company_name,
                        "location": jd.location,
                        "salary_range": jd.salary_range,
                        "summary": jd.summary,
                        "posted_at": job.created_at,
                    }
                )

        return job_items, len(job_items)

    async def generate_feed(self) -> str:
        """
        Generate XML feed for all approved jobs.
        """
        from app.careers.xml_generator import generate_xml_feed

        jobs = await self.repository.get_approved_jobs()
        # TODO: Get base URL from settings
        # Standard generic XML feeds often need the base site URL
        base_url = "http://localhost:3000"
        return generate_xml_feed(jobs, base_url)

    async def get_public_job_detail(self, job_id: UUID) -> dict | None:
        """
        Get full job details with JSON-LD for Google indexing.

        Args:
            job_id: The job UUID

        Returns:
            Job detail dict with JSON-LD, or None if not found/not approved
        """
        job = await self.repository.get_public_job(job_id)

        if not job or not job.generated_jd:
            return None

        jd = GeneratedJD.model_validate(job.generated_jd)

        # Generate JSON-LD for Google
        jsonld_data = generate_job_posting_jsonld(
            job_id=str(job.id),
            generated_jd=jd,
            company_name=job.company_name,
            company_description=job.company_description,
            date_posted=job.created_at,
        )

        return {
            "job_id": job.id,
            "job_title": jd.job_title,
            "company_name": job.company_name,
            "company_description": job.company_description,
            "location": jd.location,
            "salary_range": jd.salary_range,
            "summary": jd.summary,
            "description": jd.description,
            "responsibilities": jd.responsibilities,
            "requirements": jd.requirements,
            "nice_to_have": jd.nice_to_have,
            "benefits": jd.benefits,
            "posted_at": job.created_at,
            "jsonld": jsonld_data.jsonld,
        }
