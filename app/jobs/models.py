"""
Jobs App Database Models
"""

from sqlalchemy import Column, String, DateTime, Index, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class JobRecord(Base):
    """Persistent job record."""

    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True)
    thread_id = Column(String(255), unique=True, index=True)
    role_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    company_description = Column(Text, nullable=True)  # For JSON-LD
    current_node = Column(String(50), nullable=False, index=True)
    jd_approval_status = Column(
        String(20), nullable=False, default="pending", index=True
    )
    generated_jd = Column(JSONB, nullable=True)  # Store complete JD for public access
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Relationships
    applicants = relationship(
        "ApplicantRecord",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_jobs_node_created", "current_node", "created_at"),
        Index("ix_jobs_approval_status", "jd_approval_status"),
    )
