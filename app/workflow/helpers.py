"""
Workflow Helper Functions

Reusable utilities for workflow operations. Extracts common patterns
to keep node functions and engine focused and DRY.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from app.jobs.schemas import ApprovalStatus, JobInput
from app.candidates.schemas import Applicant
from app.interviews.schemas import PrescreeningQuestion
from app.workflow.state import GraphState
from app.workflow.constants import NodeName


# =============================================================================
# State Conversion Helpers (LangGraph <-> Pydantic)
# =============================================================================

def dict_to_graph_state(data: dict[str, Any]) -> GraphState:
    """
    Convert a dictionary (from LangGraph checkpointer) to a GraphState Pydantic model.
    
    LangGraph stores/returns state as dicts, so we need to reconstruct the Pydantic model.
    
    Args:
        data: Dictionary representation of state from LangGraph
        
    Returns:
        GraphState Pydantic model instance
    """
    return GraphState.model_validate(data)


def graph_state_to_dict(state: GraphState) -> dict[str, Any]:
    """
    Convert a GraphState Pydantic model to a dictionary for LangGraph.
    
    LangGraph expects dict input for state operations.
    
    Args:
        state: GraphState Pydantic model (or dict if already converted)
        
    Returns:
        Dictionary representation of state for LangGraph
    """
    if isinstance(state, dict):
        return state
    return state.model_dump(mode="python")


# =============================================================================
# Timestamp Helpers
# =============================================================================

def update_node_and_timestamp(state: GraphState, node: str) -> None:
    """Update current node and timestamp atomically."""
    state.current_node = node
    state.updated_at = datetime.now(timezone.utc)


# =============================================================================
# JD Generation Helpers
# =============================================================================

def should_skip_jd_generation(state: GraphState) -> bool:
    """Check if JD generation should be skipped (e.g., resuming after approval)."""
    return state.jd.bypass_generation


def prepare_for_jd_generation(state: GraphState) -> None:
    """Set up state for JD generation."""
    state.current_node = NodeName.GENERATE_JD.value
    state.jd.approval_status = ApprovalStatus.PENDING
    state.jd.generation_attempts += 1
    state.updated_at = datetime.now(timezone.utc)


def initialize_prescreening_questions(state: GraphState, job_input: JobInput) -> None:
    """Create prescreening questions from job input if not already set."""
    if not state.prescreening.questions and job_input.prescreening_questions:
        state.prescreening.questions = [
            PrescreeningQuestion(
                id=uuid4(),
                question_text=q,
                expected_keywords=[],
                max_score=100,
            )
            for q in job_input.prescreening_questions
        ]


# =============================================================================
# Applicant Helpers
# =============================================================================

def get_shortlisted_applicants(state: GraphState) -> list[Applicant]:
    """Get applicants that are in the shortlist."""
    shortlisted_ids = set(state.applicants.shortlisted_ids)
    return [a for a in state.applicants.applicants if str(a.id) in shortlisted_ids]


def filter_candidates_by_threshold(
    ranked_candidates: list[Applicant],
    threshold: float | None = None,
) -> list[str]:
    """
    Filter candidates by similarity threshold and return their IDs.
    
    Args:
        ranked_candidates: List of candidates with similarity scores
        threshold: Minimum similarity score (defaults to settings value)
        
    Returns:
        List of candidate IDs that meet the threshold
    """
    if threshold is None:
        settings = get_settings()
        threshold = settings.shortlist_similarity_threshold
    
    return [
        str(a.id)
        for a in ranked_candidates
        if a.similarity_score and a.similarity_score >= threshold
    ]


# =============================================================================
# Prescreening Helpers
# =============================================================================

def has_prescreening_data(state: GraphState) -> bool:
    """Check if state has data needed for prescreening."""
    return bool(state.applicants.shortlisted_ids and state.prescreening.questions)
