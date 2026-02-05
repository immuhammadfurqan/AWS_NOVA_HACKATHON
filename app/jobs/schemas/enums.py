"""
Enum types for Jobs module.
"""

from enum import Enum


class RecruitmentNodeStatus(str, Enum):
    """Current node in the recruitment graph."""

    PENDING = "pending"
    GENERATE_JD = "generate_jd"
    JD_REVIEW = "jd_review"
    POST_JOB = "post_job"
    MONITOR_APPLICATIONS = "monitor_applications"
    SHORTLIST_CANDIDATES = "shortlist_candidates"
    VOICE_PRESCREENING = "voice_prescreening"
    REVIEW_RESPONSES = "review_responses"
    SCHEDULE_INTERVIEW = "schedule_interview"
    REJECT_CANDIDATE = "reject_candidate"
    COMPLETED = "completed"


class ApprovalStatus(str, Enum):
    """Human-in-the-loop approval status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
