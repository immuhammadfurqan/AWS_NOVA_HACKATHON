"""
Interviews App Database Models
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class InterviewRecord(Base):
    """Persistent interview schedule record."""

    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True)
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("applicants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_datetime = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    meeting_link = Column(Text)
    calendar_event_id = Column(String(255))
    interviewer_email = Column(String(255))
    status = Column(String(50), default="pending", index=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    candidate = relationship("ApplicantRecord")
    job = relationship("JobRecord")

    # Composite index for querying schedules
    __table_args__ = (Index("ix_interviews_job_status", "job_id", "status"),)
