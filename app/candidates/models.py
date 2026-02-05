"""
Candidates App Database Models
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    DateTime,
    Boolean,
    Integer,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ApplicantRecord(Base):
    """Persistent applicant record with vector embedding."""

    __tablename__ = "applicants"

    id = Column(UUID(as_uuid=True), primary_key=True)
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50))
    resume_path = Column(Text)
    resume_text = Column(Text)
    similarity_score = Column(Float, index=True)
    shortlisted = Column(Boolean, default=False)
    applied_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relationships
    job = relationship("JobRecord", back_populates="applicants")
    prescreening_responses = relationship(
        "PrescreeningResponseRecord",
        back_populates="candidate",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_applicants_job_shortlist", "job_id", "shortlisted"),
        Index("ix_applicants_job_score", "job_id", "similarity_score"),
        Index(
            "ix_applicants_email_job", "email", "job_id", unique=True
        ),  # Prevent duplicate applications
    )


class PrescreeningResponseRecord(Base):
    """Persistent prescreening response record."""

    __tablename__ = "prescreening_responses"

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
    question_id = Column(UUID(as_uuid=True), nullable=False)
    question_text = Column(Text, nullable=False)
    transcript = Column(Text, nullable=False)
    audio_url = Column(Text)
    ai_score = Column(Integer, default=0)
    scoring_rationale = Column(Text)
    call_duration_seconds = Column(Integer)
    recorded_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    candidate = relationship("ApplicantRecord", back_populates="prescreening_responses")

    # Composite index
    __table_args__ = (Index("ix_responses_candidate_job", "candidate_id", "job_id"),)
