"""
AARLP Workflow Package

LangGraph-based recruitment workflow orchestration.
This package contains the state machine that powers the entire
JD-to-Interview recruitment pipeline.

Modules:
- constants: NodeName enum and workflow constants
- state: GraphState TypedDict and initial state factory
- nodes: Workflow node functions (generate_jd, post_job, etc.)
- edges: Conditional routing functions
- builder: Graph construction and compilation
- checkpoints: State persistence helpers
- engine: High-level workflow abstraction
- exceptions: Workflow-specific exception types
"""

from app.workflow.constants import (
    NodeName,
    WAIT_FOR_HUMAN,
    MAX_JD_GENERATION_ATTEMPTS,
    DEFAULT_MIN_APPLICANT_THRESHOLD,
    DEFAULT_SHORTLIST_SIMILARITY_THRESHOLD,
)
from app.workflow.state import (
    GraphState,
    JobDescriptionState,
    JobPostingState,
    ApplicantState,
    PrescreeningState,
    InterviewState,
    create_initial_state,
    validate_state_for_node,
)
from app.workflow.builder import get_recruitment_graph, build_recruitment_graph
from app.workflow.checkpoints import get_state_from_checkpoint, save_state_to_checkpoint
from app.workflow.engine import WorkflowEngine
from app.workflow.exceptions import (
    GraphError,
    GraphExecutionError,
    InvalidStateTransitionError,
    JDGenerationError,
    JobPostingError,
    ApplicationMonitoringError,
    ShortlistingError,
    PrescreeningError,
    SchedulingError,
    FeatureNotImplementedError,
)

__all__ = [
    # Constants
    "NodeName",
    "WAIT_FOR_HUMAN",
    "MAX_JD_GENERATION_ATTEMPTS",
    "DEFAULT_MIN_APPLICANT_THRESHOLD",
    "DEFAULT_SHORTLIST_SIMILARITY_THRESHOLD",
    # State types
    "GraphState",
    "JobDescriptionState",
    "JobPostingState",
    "ApplicantState",
    "PrescreeningState",
    "InterviewState",
    # Factory functions
    "create_initial_state",
    "validate_state_for_node",
    # Graph builders
    "get_recruitment_graph",
    "build_recruitment_graph",
    # Checkpoint helpers
    "get_state_from_checkpoint",
    "save_state_to_checkpoint",
    # Engine
    "WorkflowEngine",
    # Exceptions
    "GraphError",
    "GraphExecutionError",
    "InvalidStateTransitionError",
    "JDGenerationError",
    "JobPostingError",
    "ApplicationMonitoringError",
    "ShortlistingError",
    "PrescreeningError",
    "SchedulingError",
    "FeatureNotImplementedError",
]
