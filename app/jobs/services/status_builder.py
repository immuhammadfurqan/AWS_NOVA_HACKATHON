"""
Status builder service.

Builds JobStatusResponse from various sources.
"""

from uuid import UUID

from app.jobs.schemas import JobStatusResponse, RecruitmentNodeStatus, ApprovalStatus
from app.jobs.models import JobRecord
from app.workflow import GraphState


class StatusBuilder:
    """
    Builds JobStatusResponse from state or DB record.

    Single Responsibility: Status response construction.
    """

    @staticmethod
    def from_state(state: GraphState) -> JobStatusResponse:
        """Build status from workflow state."""
        return JobStatusResponse(
            job_id=UUID(state.job_id),
            current_node=RecruitmentNodeStatus(state.current_node),
            applicant_count=len(state.applicants.applicants),
            shortlisted_count=len(state.applicants.shortlisted_ids),
            shortlist_approval_status=state.applicants.shortlist_approval,
            jd_approval_status=state.jd.approval_status,
            prescreening_complete=state.prescreening.is_complete,
            scheduled_interviews_count=len(state.interviews.scheduled),
            has_generated_jd=state.jd.generated_jd is not None,
            error_message=state.error_message,
            created_at=state.created_at,
            updated_at=state.updated_at,
        )

    @staticmethod
    def from_record(job_record: JobRecord) -> JobStatusResponse:
        """Build fallback status from DB record."""
        return JobStatusResponse(
            job_id=job_record.id,
            current_node=RecruitmentNodeStatus(job_record.current_node),
            applicant_count=0,
            shortlisted_count=0,
            shortlist_approval_status=ApprovalStatus.PENDING,
            jd_approval_status=ApprovalStatus.PENDING,
            prescreening_complete=False,
            scheduled_interviews_count=0,
            has_generated_jd=False,
            created_at=job_record.created_at,
            updated_at=job_record.updated_at,
        )
