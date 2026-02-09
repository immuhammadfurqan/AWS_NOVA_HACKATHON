"""
Workflow Node Functions

Each node represents a step in the recruitment pipeline.
Nodes modify state and return the updated state.
"""

from datetime import datetime, timezone

from pydantic import ValidationError

from app.core.config import get_settings
from app.jobs.schemas import RecruitmentNodeStatus, ApprovalStatus
from app.ai.jd_generator import generate_job_description, optimize_job_description
from app.workflow.state import GraphState
from app.workflow.constants import NodeName
from app.workflow.exceptions import (
    JDGenerationError,
    JobPostingError,
    ApplicationMonitoringError,
    ShortlistingError,
    PrescreeningError,
    SchedulingError,
    FeatureNotImplementedError,
)
from app.workflow.helpers import (
    update_node_and_timestamp,
    should_skip_jd_generation,
    prepare_for_jd_generation,
    initialize_prescreening_questions,
    get_shortlisted_applicants,
    filter_candidates_by_threshold,
    has_prescreening_data,
)
from app.ai.embeddings import rank_candidates_by_similarity
from app.ai.voice_agent import conduct_prescreening_calls
from app.interviews.scheduler import schedule_interviews


# =============================================================================
# JD Generation Node
# =============================================================================


async def generate_jd_node(state: GraphState) -> GraphState:
    """
    Generate job description using AI.

    This node:
    1. Checks if generation should be skipped (bypass flag)
    2. Calls AI to generate JD from job input
    3. Initializes prescreening questions if provided
    4. Transitions to JD review state
    """
    if should_skip_jd_generation(state):
        state.jd.bypass_generation = False
        return state

    prepare_for_jd_generation(state)

    try:
        job_input = state.jd.input
        generated_jd = await generate_job_description(job_input)
        state.jd.generated_jd = generated_jd

        initialize_prescreening_questions(state, job_input)
        state.current_node = RecruitmentNodeStatus.JD_REVIEW.value

    except ValidationError as e:
        raise JDGenerationError(f"Invalid job input: {e}")
    except Exception as e:
        raise JDGenerationError(str(e))

    return state


async def optimize_jd_node(state: GraphState) -> GraphState:
    """
    Optimize an existing JD when candidate count is low.

    This node:
    1. Increments generation attempts
    2. Calls AI to optimize the JD
    3. Updates the JD in state
    4. Resets posting timestamp to trigger re-indexing
    """
    if not state.jd.generated_jd:
        raise JDGenerationError("Cannot optimize JD: No existing JD found.")

    try:
        # Increment attempts counter
        state.jd.generation_attempts += 1

        # Optimize JD
        optimized_jd = await optimize_job_description(state.jd.generated_jd)
        state.jd.generated_jd = optimized_jd

        # Mark for re-posting/update
        # We don't need to change is_posted to False if we just update the content
        # But updating posted_at signals a new version
        state.posting.posted_at = datetime.now(timezone.utc)

        # Reset generation bypass flag to ensure we don't skip future steps if logic changes
        state.jd.bypass_generation = False

        # Reset approval status?
        # User said "re-upload by their own", implying auto-approval.
        # But for safety, we might want to keep it APPROVED since AI did it based on existing approved JD?
        # If we go to POST_JOB directly, we skip approval check anyway (if edge allows).
        # Let's keep approval as APPROVED or PENDING?
        # If we loop to POST_JOB, check_jd_approval is NOT called (that's only after GENERATE).
        # So it's fine.

    except Exception as e:
        raise JDGenerationError(f"JD Optimization failed: {str(e)}")

    return state


# =============================================================================
# Job Posting Node
# =============================================================================


async def post_job_node(state: GraphState) -> GraphState:
    """
    Post the job to job boards.

    With Google for Jobs integration, the job is automatically available
    on public /careers endpoint with JSON-LD structured data for Google indexing.
    No browser automation required - Google crawls and indexes the page.
    """
    update_node_and_timestamp(state, NodeName.POST_JOB.value)

    # With Google for Jobs integration, the approved JD is now available
    # on the public /careers/{job_id} endpoint with JSON-LD structured data.
    # Google will automatically crawl and index this page.
    state.posting.is_posted = True
    state.posting.posted_at = datetime.now(timezone.utc)
    state.posting.posting_url = f"/careers/{state.job_id}"  # Public careers page URL

    return state


# =============================================================================
# Application Monitoring Node
# =============================================================================


async def monitor_applications_node(state: GraphState) -> GraphState:
    """
    Monitor incoming applications from job boards.

    With Google for Jobs integration, applications come through manually
    (applicants apply via email/form linked on the careers page).
    This node marks monitoring as started and waits for applicants to be added.
    """
    update_node_and_timestamp(state, NodeName.MONITOR_APPLICATIONS.value)

    if not state.applicants.monitoring_start:
        state.applicants.monitoring_start = datetime.now(timezone.utc)

    # With Google for Jobs, applicants come in through manual channels
    # (email, forms, etc.) and are added via the API.
    # Mark monitoring as active - actual applicant processing happens
    # when applicants are added through the API.
    state.applicants.monitoring_complete = True

    return state


# =============================================================================
# Shortlisting Node
# =============================================================================


def _rank_and_store_candidates(state: GraphState, ranked: list) -> None:
    """Store ranked candidates and update shortlist."""
    state.applicants.applicants = ranked
    state.applicants.shortlisted_ids = filter_candidates_by_threshold(ranked)


async def shortlist_candidates_node(state: GraphState) -> GraphState:
    """
    Semantically shortlist candidates using pgvector similarity.

    This node:
    1. Validates JD exists
    2. Ranks candidates by semantic similarity to JD
    3. Auto-shortlists candidates above threshold
    """
    update_node_and_timestamp(state, NodeName.SHORTLIST_CANDIDATES.value)

    try:
        if not state.applicants.applicants:
            return state

        jd = state.jd.generated_jd
        if not jd:
            raise ShortlistingError("No job description available for shortlisting")

        # Rank candidates by semantic similarity
        ranked = await rank_candidates_by_similarity(jd, state.applicants.applicants)
        _rank_and_store_candidates(state, ranked)

    except ShortlistingError:
        raise
    except ValidationError as e:
        raise ShortlistingError(f"Invalid data format: {e}")
    except Exception as e:
        raise ShortlistingError(str(e))

    return state


# =============================================================================
# Voice Prescreening Node
# =============================================================================


def _store_prescreening_responses(state: GraphState, responses: dict) -> None:
    """Store prescreening responses by candidate ID."""
    for candidate_id, candidate_responses in responses.items():
        state.prescreening.responses[candidate_id] = candidate_responses


async def voice_prescreening_node(state: GraphState) -> GraphState:
    """
    Conduct AI voice prescreening calls with shortlisted candidates.

    This node:
    1. Gets shortlisted candidates
    2. Conducts voice calls with prescreening questions
    3. Stores responses for each candidate
    """
    update_node_and_timestamp(state, NodeName.VOICE_PRESCREENING.value)

    try:
        if has_prescreening_data(state):
            shortlisted = get_shortlisted_applicants(state)
            questions = state.prescreening.questions

            # Conduct calls and collect responses
            responses = await conduct_prescreening_calls(shortlisted, questions)
            _store_prescreening_responses(state, responses)

        state.prescreening.is_complete = True

    except ValidationError as e:
        raise PrescreeningError(f"Invalid data format: {e}")
    except Exception as e:
        raise PrescreeningError(str(e))

    return state


# =============================================================================
# Review Responses Node
# =============================================================================


async def review_responses_node(state: GraphState) -> GraphState:
    """Present prescreening responses to recruiter for review."""
    update_node_and_timestamp(state, NodeName.REVIEW_RESPONSES.value)
    return state


# =============================================================================
# Schedule Interview Node
# =============================================================================


async def schedule_interview_node(state: GraphState) -> GraphState:
    """
    Schedule technical interviews for approved candidates.

    This node schedules interviews for all shortlisted candidates
    using the configured interview scheduler.
    """
    update_node_and_timestamp(state, NodeName.SCHEDULE_INTERVIEW.value)

    try:
        approved_candidates = get_shortlisted_applicants(state)

        if approved_candidates:
            interviews = await schedule_interviews(state.job_id, approved_candidates)
            state.interviews.scheduled = interviews

    except ValidationError as e:
        raise SchedulingError(f"Invalid candidate data: {e}")
    except Exception as e:
        raise SchedulingError(str(e))

    return state


# =============================================================================
# Reject Candidate Node
# =============================================================================


async def reject_candidate_node(state: GraphState) -> GraphState:
    """Handle candidate rejection after prescreening."""
    update_node_and_timestamp(state, NodeName.REJECT_CANDIDATE.value)
    return state
