"""
Workflow Engine Exceptions

Provides specific exception types for each workflow node failure,
enabling precise error handling and meaningful error messages.
"""

from typing import Optional
from app.core.exceptions import AARLPException
from app.workflow.constants import NodeName


class GraphError(AARLPException):
    """Base exception for LangGraph workflow errors."""

    def __init__(self, message: str, node: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            error_code="GRAPH_ERROR",
            details={"node": node} if node else {},
        )


class InvalidStateTransitionError(GraphError):
    """Raised when an invalid state transition is attempted."""

    def __init__(
        self,
        current_node: str,
        attempted_action: str,
        allowed_actions: list[str],
    ) -> None:
        super().__init__(
            message=f"Cannot perform '{attempted_action}' while in '{current_node}' state",
            node=current_node,
        )
        self.error_code = "INVALID_TRANSITION"
        self.details = {
            "current_node": current_node,
            "attempted_action": attempted_action,
            "allowed_actions": allowed_actions,
        }


class GraphExecutionError(GraphError):
    """Raised when graph execution fails."""

    def __init__(
        self, message: str, node: str, original_error: Optional[str] = None
    ) -> None:
        super().__init__(message=message, node=node)
        self.error_code = "GRAPH_EXECUTION_ERROR"
        self.details["original_error"] = original_error


# =============================================================================
# Node-Specific Exceptions
# =============================================================================

class JDGenerationError(GraphExecutionError):
    """Raised when job description generation fails."""

    def __init__(self, original_error: str) -> None:
        super().__init__(
            message="Job description generation failed",
            node=NodeName.GENERATE_JD.value,
            original_error=original_error,
        )
        self.error_code = "JD_GENERATION_ERROR"


class JobPostingError(GraphExecutionError):
    """Raised when job posting fails."""

    def __init__(self, original_error: str) -> None:
        super().__init__(
            message="Job posting failed",
            node=NodeName.POST_JOB.value,
            original_error=original_error,
        )
        self.error_code = "JOB_POSTING_ERROR"


class ApplicationMonitoringError(GraphExecutionError):
    """Raised when application monitoring fails."""

    def __init__(self, original_error: str) -> None:
        super().__init__(
            message="Application monitoring failed",
            node=NodeName.MONITOR_APPLICATIONS.value,
            original_error=original_error,
        )
        self.error_code = "APPLICATION_MONITORING_ERROR"


class ShortlistingError(GraphExecutionError):
    """Raised when candidate shortlisting fails."""

    def __init__(self, original_error: str) -> None:
        super().__init__(
            message="Candidate shortlisting failed",
            node=NodeName.SHORTLIST_CANDIDATES.value,
            original_error=original_error,
        )
        self.error_code = "SHORTLISTING_ERROR"


class PrescreeningError(GraphExecutionError):
    """Raised when voice prescreening fails."""

    def __init__(self, original_error: str) -> None:
        super().__init__(
            message="Voice prescreening failed",
            node=NodeName.VOICE_PRESCREENING.value,
            original_error=original_error,
        )
        self.error_code = "PRESCREENING_ERROR"


class SchedulingError(GraphExecutionError):
    """Raised when interview scheduling fails."""

    def __init__(self, original_error: str) -> None:
        super().__init__(
            message="Interview scheduling failed",
            node=NodeName.SCHEDULE_INTERVIEW.value,
            original_error=original_error,
        )
        self.error_code = "SCHEDULING_ERROR"


class FeatureNotImplementedError(GraphError):
    """Raised when a feature is not yet implemented."""

    def __init__(self, feature_name: str, node: str) -> None:
        super().__init__(
            message=f"Feature '{feature_name}' is not yet implemented",
            node=node,
        )
        self.error_code = "FEATURE_NOT_IMPLEMENTED"
        self.details["feature_name"] = feature_name
