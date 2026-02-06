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

    async def create_application(
        self,
        job_id: UUID,
        name: str,
        email: str,
        phone: str | None,
        resume_content: bytes,
        resume_filename: str,
    ) -> dict:
        """
        Process a new job application.

        1. Verify job exists and is approved
        2. Check for duplicate application
        3. Save resume file
        4. Extract text from PDF
        5. Generate embedding
        6. Create applicant record
        7. Store in Pinecone

        Returns:
            Dict with applicant_id and job_id
        """
        import os
        import tempfile
        from datetime import datetime, timezone
        from uuid import uuid4
        from pathlib import Path

        from app.ai.pdf_parser import extract_text_from_pdf, clean_resume_text
        from app.ai.embeddings import generate_embedding, PineconeService
        from app.candidates.models import ApplicantRecord

        # 1. Verify job exists and is approved
        job = await self.repository.get_public_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found or not published")

        # 2. Check for duplicate application
        existing = await self.repository.get_applicant_by_email(job_id, email)
        if existing:
            raise ValueError(
                f"An application with email {email} already exists for this job"
            )

        # 3. Save resume file to temp location
        uploads_dir = Path("uploads/resumes")
        uploads_dir.mkdir(parents=True, exist_ok=True)

        applicant_id = uuid4()
        safe_filename = f"{applicant_id}_{resume_filename}"
        resume_path = uploads_dir / safe_filename

        with open(resume_path, "wb") as f:
            f.write(resume_content)

        logger.info(f"Saved resume to {resume_path}")

        # 4. Extract text from PDF
        resume_text = await extract_text_from_pdf(str(resume_path))
        if resume_text:
            resume_text = clean_resume_text(resume_text)
        else:
            resume_text = ""
            logger.warning(f"Could not extract text from resume: {resume_filename}")

        # 5. Generate embedding
        embedding = None
        similarity_score = None
        if resume_text:
            try:
                embedding = await generate_embedding(resume_text)
                logger.info(f"Generated embedding with {len(embedding)} dimensions")

                # Calculate similarity with JD if available
                if job.generated_jd:
                    from app.ai.embeddings import generate_jd_embedding
                    import numpy as np

                    jd_obj = GeneratedJD.model_validate(job.generated_jd)
                    jd_embedding = await generate_jd_embedding(jd_obj)

                    # Cosine similarity
                    vec1 = np.array(jd_embedding)
                    vec2 = np.array(embedding)
                    dot_product = np.dot(vec1, vec2)
                    norm1 = np.linalg.norm(vec1)
                    norm2 = np.linalg.norm(vec2)
                    if norm1 > 0 and norm2 > 0:
                        similarity_score = float(dot_product / (norm1 * norm2))
                        logger.info(f"Similarity score: {similarity_score:.4f}")

            except Exception as e:
                logger.error(f"Failed to generate embedding: {e}")

        # 6. Create applicant record in database
        applicant = ApplicantRecord(
            id=applicant_id,
            job_id=job_id,
            name=name,
            email=email,
            phone=phone,
            resume_path=str(resume_path),
            resume_text=resume_text,
            similarity_score=similarity_score,
            shortlisted=False,
            applied_at=datetime.now(timezone.utc),
        )

        await self.repository.create_applicant(applicant)
        logger.info(f"Created applicant {applicant_id} for job {job_id}")

        # 7. Store in Pinecone (optional, depends on config)
        if embedding:
            try:
                from app.candidates.schemas import Applicant as ApplicantSchema

                applicant_schema = ApplicantSchema(
                    id=applicant_id,
                    name=name,
                    email=email,
                    phone=phone,
                    resume_path=str(resume_path),
                    resume_text=resume_text,
                    embedding=embedding,
                    similarity_score=similarity_score,
                    shortlisted=False,
                    applied_at=applicant.applied_at,
                )
                ps = PineconeService()
                await ps.upsert_applicant(applicant_schema, str(job_id))
                logger.info(
                    f"Stored embedding in Pinecone for applicant {applicant_id}"
                )
            except Exception as e:
                logger.warning(f"Failed to store in Pinecone (non-fatal): {e}")

        return {
            "applicant_id": applicant_id,
            "job_id": job_id,
            "message": "Application submitted successfully",
        }
