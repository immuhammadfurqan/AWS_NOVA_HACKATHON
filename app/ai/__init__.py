"""
AARLP AI Module

Centralized AI business logic for:
- Job Description generation
- Semantic embeddings and ranking
- Voice response scoring
"""

from app.ai.jd_generator import generate_job_description
from app.ai.embeddings import generate_embedding, rank_candidates_by_similarity

__all__ = [
    "generate_job_description",
    "generate_embedding",
    "rank_candidates_by_similarity",
]
