"""
AARLP Pinecone Utility

Vector embedding storage and semantic similarity matching using:
- OpenAI text-embedding-3-small (fallback)
- AWS Bedrock Nova/Titan embeddings (primary for hackathon)
- Pinecone for vector database storage and search

Provider selection is controlled by AI_PROVIDER env var.
"""

import asyncio
from typing import Optional, List, Dict, Any
from uuid import UUID

from pinecone import Pinecone, ServerlessSpec
import numpy as np

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ai.client import (
    get_openai_client,
    is_bedrock_provider,
    get_embedding_dimension,
)
from app.ai.constants import EmbeddingLimits
from app.candidates.schemas import Applicant
from app.jobs.schemas import GeneratedJD

logger = get_logger(__name__)


class PineconeService:
    """Service for interacting with Pinecone Vector DB."""

    def __init__(self, api_key: str = None, index_name: str = None):
        """
        Initialize PineconeService.

        Args:
            api_key: Pinecone API key. If None, loads from settings.
            index_name: Pinecone index name. If None, loads from settings.
        """
        settings = get_settings()
        self.api_key = api_key or settings.pinecone_api_key
        self.index_name = index_name or settings.pinecone_index

        if not self.api_key:
            raise ValueError("PINECONE_API_KEY is not set")

        self.pc = Pinecone(api_key=self.api_key)
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        """Check if index exists, if not create it with correct dimension for provider."""
        dimension = get_embedding_dimension()

        if self.index_name not in self.pc.list_indexes().names():
            logger.info(
                f"Creating Pinecone index '{self.index_name}' with dimension {dimension}"
            )
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,  # 1024 for Nova/Titan, 1536 for OpenAI
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

    async def upsert_applicant(self, applicant: Applicant, job_id: str):
        """Store applicant embedding in Pinecone."""
        if not applicant.embedding:
            return

        # Metadata to store with the vector
        metadata = {
            "job_id": str(job_id),
            "type": "applicant",
            "name": applicant.name,
            "email": applicant.email,
            "applied_at": applicant.applied_at.isoformat(),
            "shortlisted": applicant.shortlisted,
        }

        # Run blocking Pinecone operation in thread pool to avoid blocking event loop
        await asyncio.to_thread(
            self.index.upsert,
            vectors=[(str(applicant.id), applicant.embedding, metadata)],
        )

    async def query_similar_candidates(
        self, job_id: str, vector: List[float], top_k: int = 10, min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Query Pinecone for similar candidates within a specific job."""

        # Run blocking query in thread pool
        query_response = await asyncio.to_thread(
            self.index.query,
            vector=vector,
            top_k=top_k,
            filter={"job_id": {"$eq": str(job_id)}, "type": {"$eq": "applicant"}},
            include_metadata=True,
        )

        results = []
        for match in query_response.get("matches", []):
            if match["score"] >= min_score:
                results.append(
                    {
                        "id": match["id"],
                        "score": match["score"],
                        "metadata": match["metadata"],
                    }
                )
        return results

    async def delete_job_embeddings(self, job_id: str):
        """Delete all vectors associated with a specific job."""
        # Delete by metadata filter (run in thread pool)
        await asyncio.to_thread(
            self.index.delete, filter={"job_id": {"$eq": str(job_id)}}
        )

    async def upsert_job_embedding(
        self, job_id: str, embedding: List[float], metadata: Dict[str, Any]
    ):
        """Store job embedding in Pinecone."""
        # Run blocking upsert in thread pool
        await asyncio.to_thread(
            self.index.upsert, vectors=[(str(job_id), embedding, metadata)]
        )


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using configured AI provider.

    Uses OpenAI or AWS Bedrock based on AI_PROVIDER setting.

    Args:
        text: Text to embed

    Returns:
        List of floats (embedding vector)

    Raises:
        ValueError: If text is empty
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if len(text) > EmbeddingLimits.MAX_TEXT_LENGTH:
        logger.warning(
            f"Text truncated from {len(text)} to {EmbeddingLimits.MAX_TEXT_LENGTH}"
        )
        text = text[: EmbeddingLimits.MAX_TEXT_LENGTH]

    if is_bedrock_provider():
        return await _generate_embedding_bedrock(text)
    else:
        return await _generate_embedding_openai(text)


async def _generate_embedding_openai(text: str) -> List[float]:
    """Generate embedding using OpenAI."""
    settings = get_settings()
    client = get_openai_client()

    response = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text,
    )

    return response.data[0].embedding


async def _generate_embedding_bedrock(text: str) -> List[float]:
    """Generate embedding using AWS Bedrock Nova/Titan model."""
    from app.ai.bedrock_client import generate_embedding as bedrock_generate_embedding

    return await bedrock_generate_embedding(text)


async def generate_jd_embedding(jd: GeneratedJD) -> List[float]:
    """Generate embedding for a job description."""
    text_parts = [
        jd.job_title,
        jd.summary,
        jd.description,
        "Requirements: " + ", ".join(jd.requirements),
        "Nice to have: " + ", ".join(jd.nice_to_have),
    ]
    combined_text = "\n".join(text_parts)
    return await generate_embedding(combined_text)


async def rank_candidates_by_similarity(
    jd: GeneratedJD, applicants: List[Applicant]
) -> List[Applicant]:
    """Rank candidates by semantic similarity using OpenAI embeddings."""
    jd_embedding = await generate_jd_embedding(jd)

    tasks = []
    for applicant in applicants:
        if applicant.resume_text:
            tasks.append(_score_applicant(applicant, jd_embedding))
        else:
            applicant.similarity_score = 0.0

    if tasks:
        await asyncio.gather(*tasks)

    return sorted(applicants, key=lambda a: a.similarity_score or 0.0, reverse=True)


async def _score_applicant(applicant: Applicant, jd_embedding: List[float]) -> None:
    """Score a single applicant against JD embedding."""
    try:

        if not applicant.embedding:
            applicant.embedding = await generate_embedding(applicant.resume_text)

        vec1 = np.array(jd_embedding)
        vec2 = np.array(applicant.embedding)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            applicant.similarity_score = 0.0
        else:
            applicant.similarity_score = float(dot_product / (norm1 * norm2))

    except Exception as e:
        logger.error(
            "Failed to score applicant",
            extra={"applicant_id": str(applicant.id), "error": str(e)},
        )
        applicant.similarity_score = 0.0


async def store_applicant_with_embedding(
    session: Any, applicant: Applicant, job_id: str  # Kept for interface compatibility
) -> None:
    """Store applicant in Pinecone (and Postgres without embedding)."""
    # Note: ApplicantRecord in Postgres now has no embedding column.
    # The actual DB storage happens in CandidateService.
    # This utility now focuses on Pinecone.

    # Generate embedding if missing
    if not applicant.embedding and applicant.resume_text:
        applicant.embedding = await generate_embedding(applicant.resume_text)

    if applicant.embedding:
        ps = PineconeService()
        await ps.upsert_applicant(applicant, job_id)


async def find_similar_candidates(
    job_id: str, jd_embedding: List[float], limit: int = 10, min_similarity: float = 0.5
) -> List[Dict[str, Any]]:
    """Find candidates similar to the JD using Pinecone."""
    ps = PineconeService()
    return await ps.query_similar_candidates(
        job_id=job_id, vector=jd_embedding, top_k=limit, min_score=min_similarity
    )
