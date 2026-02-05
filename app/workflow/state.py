"""
Workflow State Definition

Contains the GraphState Pydantic model and factory functions for creating
initial state from job input. Uses Pydantic for full type safety and validation.
"""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional

from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.jobs.schemas import (
    RecruitmentNodeStatus,
    ApprovalStatus,
    JobInput,
    GeneratedJD,
)
from app.candidates.schemas import Applicant, CandidateResponse
from app.interviews.schemas import PrescreeningQuestion, InterviewSlot
from app.workflow.constants import NodeName


# =============================================================================
# Nested State Models (Pydantic)
# =============================================================================

class JobDescriptionState(BaseModel):
    """State related to JD generation and approval."""
    input: Optional[JobInput] = None
    generated_jd: Optional[GeneratedJD] = None
    generation_attempts: int = 0
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    feedback: Optional[str] = None
    bypass_generation: bool = False

    class Config:
        use_enum_values = False  # Keep enum objects, not just values


class JobPostingState(BaseModel):
    """State related to job posting."""
    is_posted: bool = False
    posting_url: Optional[str] = None
    posted_at: Optional[datetime] = None


class ApplicantState(BaseModel):
    """State related to applicants and shortlisting."""
    applicants: list[Applicant] = Field(default_factory=list)
    min_threshold: int = 5
    monitoring_start: Optional[datetime] = None
    monitoring_complete: bool = False
    shortlisted_ids: list[str] = Field(default_factory=list)
    shortlist_approval: ApprovalStatus = ApprovalStatus.PENDING


class PrescreeningState(BaseModel):
    """State related to prescreening."""
    questions: list[PrescreeningQuestion] = Field(default_factory=list)
    responses: dict[str, list[CandidateResponse]] = Field(default_factory=dict)
    is_complete: bool = False


class InterviewState(BaseModel):
    """State related to interviews."""
    schedule_approved: bool = False
    scheduled: list[InterviewSlot] = Field(default_factory=list)


# =============================================================================
# Main GraphState (Pydantic)
# =============================================================================

class GraphState(BaseModel):
    """
    Pydantic-based workflow state with full type safety.
    
    Benefits over TypedDict:
    - Runtime validation of all fields
    - IDE autocomplete with attribute access (state.jd.input)
    - No manual dict-to-object conversions
    - Clear error messages on validation failures
    """
    # Identifiers
    job_id: str
    thread_id: Optional[str] = None
    
    # Current Status
    current_node: str
    error_message: Optional[str] = None
    
    # Nested state groups
    jd: JobDescriptionState = Field(default_factory=JobDescriptionState)
    posting: JobPostingState = Field(default_factory=JobPostingState)
    applicants: ApplicantState = Field(default_factory=ApplicantState)
    prescreening: PrescreeningState = Field(default_factory=PrescreeningState)
    interviews: InterviewState = Field(default_factory=InterviewState)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        # Allow mutation for LangGraph compatibility
        frozen = False
        # Validate on assignment for immediate feedback
        validate_assignment = True


def create_initial_state(job_input: JobInput) -> GraphState:
    """
    Create initial graph state from job input.

    Args:
        job_input: The job creation input data

    Returns:
        GraphState: Initialized state ready for graph execution
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)

    return GraphState(
        job_id=str(uuid4()),
        thread_id=None,
        current_node=RecruitmentNodeStatus.PENDING.value,
        error_message=None,
        jd=JobDescriptionState(
            input=job_input,
            generated_jd=None,
            generation_attempts=0,
            approval_status=ApprovalStatus.PENDING,
            feedback=None,
            bypass_generation=False,
        ),
        posting=JobPostingState(
            is_posted=False,
            posting_url=None,
            posted_at=None,
        ),
        applicants=ApplicantState(
            applicants=[],
            min_threshold=settings.min_applicant_threshold,
            monitoring_start=None,
            monitoring_complete=False,
            shortlisted_ids=[],
            shortlist_approval=ApprovalStatus.PENDING,
        ),
        prescreening=PrescreeningState(
            questions=[],
            responses={},
            is_complete=False,
        ),
        interviews=InterviewState(
            schedule_approved=False,
            scheduled=[],
        ),
        created_at=now,
        updated_at=now,
    )


# =============================================================================
# State Validation
# =============================================================================

def validate_state_for_node(state: GraphState, target_node: NodeName) -> None:
    """
    Validate that state has required data for the target node.
    
    Raises InvalidStateTransitionError if validation fails.
    
    Args:
        state: Current graph state
        target_node: The node we want to transition to
    """
    validators = {
        NodeName.POST_JOB: _validate_for_posting,
        NodeName.SHORTLIST_CANDIDATES: _validate_for_shortlisting,
        NodeName.VOICE_PRESCREENING: _validate_for_prescreening,
        NodeName.SCHEDULE_INTERVIEW: _validate_for_scheduling,
    }
    
    if validator := validators.get(target_node):
        validator(state)


def _validate_for_posting(state: GraphState) -> None:
    """Validate state has approved JD before posting."""
    from app.workflow.exceptions import InvalidStateTransitionError
    
    if not state.jd.generated_jd:
        raise InvalidStateTransitionError(
            current_node=state.current_node,
            attempted_action=NodeName.POST_JOB.value,
            allowed_actions=[NodeName.GENERATE_JD.value],
        )
    
    if state.jd.approval_status != ApprovalStatus.APPROVED:
        raise InvalidStateTransitionError(
            current_node=state.current_node,
            attempted_action=NodeName.POST_JOB.value,
            allowed_actions=["approve_jd"],
        )


def _validate_for_shortlisting(state: GraphState) -> None:
    """Validate state has posted job and applicants before shortlisting."""
    from app.workflow.exceptions import InvalidStateTransitionError
    
    if not state.posting.is_posted:
        raise InvalidStateTransitionError(
            current_node=state.current_node,
            attempted_action=NodeName.SHORTLIST_CANDIDATES.value,
            allowed_actions=[NodeName.POST_JOB.value],
        )
    
    if not state.applicants.applicants:
        raise InvalidStateTransitionError(
            current_node=state.current_node,
            attempted_action=NodeName.SHORTLIST_CANDIDATES.value,
            allowed_actions=[NodeName.MONITOR_APPLICATIONS.value],
        )


def _validate_for_prescreening(state: GraphState) -> None:
    """Validate state has approved shortlist before prescreening."""
    from app.workflow.exceptions import InvalidStateTransitionError
    
    if not state.applicants.shortlisted_ids:
        raise InvalidStateTransitionError(
            current_node=state.current_node,
            attempted_action=NodeName.VOICE_PRESCREENING.value,
            allowed_actions=[NodeName.SHORTLIST_CANDIDATES.value],
        )
    
    if state.applicants.shortlist_approval != ApprovalStatus.APPROVED:
        raise InvalidStateTransitionError(
            current_node=state.current_node,
            attempted_action=NodeName.VOICE_PRESCREENING.value,
            allowed_actions=["approve_shortlist"],
        )


def _validate_for_scheduling(state: GraphState) -> None:
    """Validate state has completed prescreening before scheduling."""
    from app.workflow.exceptions import InvalidStateTransitionError
    
    if not state.prescreening.is_complete:
        raise InvalidStateTransitionError(
            current_node=state.current_node,
            attempted_action=NodeName.SCHEDULE_INTERVIEW.value,
            allowed_actions=[NodeName.VOICE_PRESCREENING.value],
        )
    
    if not state.interviews.schedule_approved:
        raise InvalidStateTransitionError(
            current_node=state.current_node,
            attempted_action=NodeName.SCHEDULE_INTERVIEW.value,
            allowed_actions=["approve_schedule"],
        )
