"""
Candidates App Schemas
"""

from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr

class Applicant(BaseModel):
    """Candidate who has applied for a job."""
    
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr
    phone: str | None = None
    resume_path: str | None = Field(default=None, description="Path to the resume PDF file")
    resume_text: str | None = Field(default=None, description="Extracted text from resume")
    embedding: list[float] | None = Field(default=None, description="Vector embedding of resume")
    similarity_score: float | None = Field(default=None, ge=0.0, le=1.0, description="Semantic similarity to JD")
    shortlisted: bool = False
    applied_at: datetime = Field(default_factory=datetime.utcnow)

class CandidateResponse(BaseModel):
    """Voice call response from a candidate."""
    
    id: UUID = Field(default_factory=uuid4)
    candidate_id: UUID
    question_id: UUID
    question_text: str
    transcript: str = Field(..., description="Transcribed response")
    audio_url: str | None = Field(default=None, description="URL to the recorded audio")
    ai_score: int = Field(default=0, ge=0, le=100, description="AI-assigned score based on keywords")
    scoring_rationale: str | None = Field(default=None, description="Explanation for the score")
    call_duration_seconds: int | None = None
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

class CandidateResponsesResponse(BaseModel):
    """Response containing candidate prescreening responses."""
    
    candidate_id: UUID
    candidate_name: str
    candidate_email: str
    total_score: int
    max_possible_score: int
    percentage_score: float
    responses: list[CandidateResponse]

class ScheduleInterviewRequest(BaseModel):
    """Request to schedule a technical interview."""
    interviewer_email: EmailStr
    preferred_datetime: datetime
