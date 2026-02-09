"""
Workflow Constants

Centralized location for all workflow-related constants, enums,
and magic values. Import from here to avoid magic strings.
"""

from enum import Enum


class NodeName(str, Enum):
    """
    Node identifiers for graph routing.

    Using an enum eliminates magic strings and provides:
    - IDE autocomplete
    - Compile-time typo detection
    - Single source of truth for node names
    """

    GENERATE_JD = "generate_jd"
    POST_JOB = "post_job"
    MONITOR_APPLICATIONS = "monitor_applications"
    SHORTLIST_CANDIDATES = "shortlist_candidates"
    VOICE_PRESCREENING = "voice_prescreening"
    REVIEW_RESPONSES = "review_responses"
    SCHEDULE_INTERVIEW = "schedule_interview"
    REJECT_CANDIDATE = "reject_candidate"
    OPTIMIZE_JD = "optimize_jd"


# =============================================================================
# Routing Constants
# =============================================================================

# Special routing value for human-in-the-loop pauses
WAIT_FOR_HUMAN = "__wait__"


# =============================================================================
# Workflow Limits
# =============================================================================

# Maximum number of JD regeneration attempts before giving up
MAX_JD_GENERATION_ATTEMPTS = 3

# Default minimum applicants needed before proceeding to shortlisting
DEFAULT_MIN_APPLICANT_THRESHOLD = 5

# Default similarity threshold for auto-shortlisting candidates
DEFAULT_SHORTLIST_SIMILARITY_THRESHOLD = 0.7
