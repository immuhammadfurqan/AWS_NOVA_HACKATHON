"""
Workflow Conditional Edge Functions

Edge functions determine workflow routing based on state.
They return the name of the next node to execute.
"""

from typing import Literal

from app.core.config import get_settings
from app.jobs.schemas import ApprovalStatus
from app.workflow.state import GraphState
from app.workflow.constants import NodeName, WAIT_FOR_HUMAN


# Type aliases for edge return types
JDApprovalRoute = Literal["post_job", "__wait__"]
RegenerateRoute = Literal[
    "generate_jd", "shortlist_candidates", "optimize_jd", "__wait__"
]
ShortlistApprovalRoute = Literal["voice_prescreening", "__wait__"]
RecruiterDecisionRoute = Literal["schedule_interview", "reject_candidate"]


def should_regenerate_jd(state: GraphState) -> RegenerateRoute:
    """
    Decide whether to regenerate/optimize JD based on applicant count.

    If insufficient applicants and max attempts not reached, optimize.
    Otherwise, proceed to shortlisting.
    """
    applicant_count = len(state.applicants.applicants)
    threshold = state.applicants.min_threshold
    attempts = state.jd.generation_attempts
    settings = get_settings()
    max_attempts = settings.max_jd_generation_attempts

    if applicant_count < threshold and attempts < max_attempts:
        # Instead of waiting, automatically optimize and re-post
        return NodeName.OPTIMIZE_JD.value

    return NodeName.SHORTLIST_CANDIDATES.value


def check_jd_approval(state: GraphState) -> JDApprovalRoute:
    """
    Check if human has approved the generated JD.

    Returns WAIT_FOR_HUMAN to pause graph execution until approval.
    """
    if state.jd.approval_status == ApprovalStatus.APPROVED:
        return NodeName.POST_JOB.value

    return WAIT_FOR_HUMAN


def check_shortlist_approval(state: GraphState) -> ShortlistApprovalRoute:
    """
    Check if human has approved the shortlist.

    Returns WAIT_FOR_HUMAN to pause graph execution until approval.
    """
    if state.applicants.shortlist_approval == ApprovalStatus.APPROVED:
        return NodeName.VOICE_PRESCREENING.value

    return WAIT_FOR_HUMAN


def recruiter_decision(state: GraphState) -> RecruiterDecisionRoute:
    """
    Route based on recruiter's decision after reviewing prescreening responses.
    """
    if state.interviews.schedule_approved:
        return NodeName.SCHEDULE_INTERVIEW.value

    return NodeName.REJECT_CANDIDATE.value
