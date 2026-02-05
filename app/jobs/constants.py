"""
Jobs Module Constants

Centralized constants for timeouts, limits, and lock key construction.
Eliminates magic numbers and provides single source of truth.
"""


class LockTimeouts:
    """Distributed lock timeout values in seconds."""

    JOB_APPROVAL = 30
    JOB_GRAPH_EXECUTION = 600
    SHORTLIST_APPROVAL = 30


class MockDataLimits:
    """Limits for mock/test data generation."""

    MIN_APPLICANTS = 1
    MAX_APPLICANTS = 100
    DEFAULT_APPLICANTS = 5


class LockKeys:
    """Factory for distributed lock keys."""

    @staticmethod
    def job_approval(job_id: str) -> str:
        """Lock key for JD approval operations."""
        return f"job:approve:{job_id}"

    @staticmethod
    def job_graph(job_id: str) -> str:
        """Lock key for graph execution operations."""
        return f"job:graph:{job_id}"

    @staticmethod
    def shortlist_approval(job_id: str) -> str:
        """Lock key for shortlist approval operations."""
        return f"job:approve_shortlist:{job_id}"
