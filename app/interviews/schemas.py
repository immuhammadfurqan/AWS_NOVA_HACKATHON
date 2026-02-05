"""
Interviews App Schemas
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr

class InterviewStatus(str, Enum):
    """Status of a scheduled interview."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PrescreeningQuestion(BaseModel):
    """Template for a prescreening question."""
    
    id: UUID = Field(default_factory=uuid4)
    question_text: str = Field(..., description="The question to ask the candidate")
    expected_keywords: list[str] = Field(default_factory=list, description="Keywords expected in a good answer")
    max_score: int = Field(default=100, ge=0, le=100, description="Maximum score for this question")

class InterviewSlot(BaseModel):
    """Scheduled interview details."""
    
    id: UUID = Field(default_factory=uuid4)
    candidate_id: UUID
    job_id: UUID
    scheduled_datetime: datetime
    duration_minutes: int = Field(default=60)
    meeting_link: str | None = Field(default=None, description="Google Meet or video call link")
    calendar_event_id: str | None = Field(default=None, description="Google Calendar event ID")
    interviewer_email: EmailStr | None = None
    status: InterviewStatus = InterviewStatus.PENDING
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
