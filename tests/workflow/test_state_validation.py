"""
Unit Tests for State Validation Functions

Tests the validate_state_for_node function and its validators.
"""

import pytest
from uuid import uuid4

from app.jobs.schemas import JobInput, GeneratedJD, ApprovalStatus
from app.candidates.schemas import Applicant
from app.workflow.state import (
    GraphState,
    create_initial_state,
    validate_state_for_node,
)
from app.workflow.constants import NodeName
from app.workflow.exceptions import InvalidStateTransitionError


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_job_input() -> JobInput:
    """Create a sample job input for testing."""
    return JobInput(
        role_title="Senior Backend Engineer",
        department="Engineering",
        company_name="TestCorp",
    )


@pytest.fixture
def sample_generated_jd() -> GeneratedJD:
    """Create a sample generated JD for testing."""
    return GeneratedJD(
        job_title="Senior Backend Engineer",
        summary="Looking for a great engineer...",
        description="Full description here...",
        responsibilities=["Build APIs"],
        requirements=["5+ years Python"],
        nice_to_have=[],
        benefits=[],
        seo_keywords=["python"],
    )


@pytest.fixture
def sample_applicant() -> Applicant:
    """Create a sample applicant for testing."""
    return Applicant(
        id=uuid4(),
        name="Alice",
        email="alice@test.com",
        resume_text="Python expert",
    )


@pytest.fixture
def initial_state(sample_job_input: JobInput) -> GraphState:
    """Create initial state for testing."""
    return create_initial_state(sample_job_input)


# =============================================================================
# Test Validate for POST_JOB
# =============================================================================

class TestValidateForPosting:
    """Tests for _validate_for_posting function."""

    def test_raises_when_no_generated_jd(self, initial_state: GraphState):
        """Test that error is raised when no JD is generated."""
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_state_for_node(initial_state, NodeName.POST_JOB)
        
        assert exc_info.value.details["attempted_action"] == NodeName.POST_JOB.value
        assert NodeName.GENERATE_JD.value in exc_info.value.details["allowed_actions"]

    def test_raises_when_jd_not_approved(
        self, 
        initial_state: GraphState, 
        sample_generated_jd: GeneratedJD,
    ):
        """Test that error is raised when JD exists but not approved."""
        initial_state.jd.generated_jd = sample_generated_jd
        initial_state.jd.approval_status = ApprovalStatus.PENDING
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_state_for_node(initial_state, NodeName.POST_JOB)
        
        assert "approve_jd" in exc_info.value.details["allowed_actions"]

    def test_passes_when_jd_approved(
        self, 
        initial_state: GraphState, 
        sample_generated_jd: GeneratedJD,
    ):
        """Test that validation passes when JD is approved."""
        initial_state.jd.generated_jd = sample_generated_jd
        initial_state.jd.approval_status = ApprovalStatus.APPROVED
        
        # Should not raise
        validate_state_for_node(initial_state, NodeName.POST_JOB)


# =============================================================================
# Test Validate for SHORTLIST_CANDIDATES
# =============================================================================

class TestValidateForShortlisting:
    """Tests for _validate_for_shortlisting function."""

    def test_raises_when_job_not_posted(
        self, 
        initial_state: GraphState,
        sample_applicant: Applicant,
    ):
        """Test that error is raised when job not posted."""
        initial_state.applicants.applicants = [sample_applicant]
        initial_state.posting.is_posted = False
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_state_for_node(initial_state, NodeName.SHORTLIST_CANDIDATES)
        
        assert NodeName.POST_JOB.value in exc_info.value.details["allowed_actions"]

    def test_raises_when_no_applicants(self, initial_state: GraphState):
        """Test that error is raised when no applicants."""
        initial_state.posting.is_posted = True
        initial_state.applicants.applicants = []
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_state_for_node(initial_state, NodeName.SHORTLIST_CANDIDATES)
        
        assert NodeName.MONITOR_APPLICATIONS.value in exc_info.value.details["allowed_actions"]

    def test_passes_when_job_posted_and_has_applicants(
        self, 
        initial_state: GraphState,
        sample_applicant: Applicant,
    ):
        """Test that validation passes when conditions are met."""
        initial_state.posting.is_posted = True
        initial_state.applicants.applicants = [sample_applicant]
        
        # Should not raise
        validate_state_for_node(initial_state, NodeName.SHORTLIST_CANDIDATES)


# =============================================================================
# Test Validate for VOICE_PRESCREENING
# =============================================================================

class TestValidateForPrescreening:
    """Tests for _validate_for_prescreening function."""

    def test_raises_when_no_shortlisted_candidates(self, initial_state: GraphState):
        """Test that error is raised when no shortlisted candidates."""
        initial_state.applicants.shortlisted_ids = []
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_state_for_node(initial_state, NodeName.VOICE_PRESCREENING)
        
        assert NodeName.SHORTLIST_CANDIDATES.value in exc_info.value.details["allowed_actions"]

    def test_raises_when_shortlist_not_approved(
        self, 
        initial_state: GraphState,
        sample_applicant: Applicant,
    ):
        """Test that error is raised when shortlist not approved."""
        initial_state.applicants.shortlisted_ids = [str(sample_applicant.id)]
        initial_state.applicants.shortlist_approval = ApprovalStatus.PENDING
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_state_for_node(initial_state, NodeName.VOICE_PRESCREENING)
        
        assert "approve_shortlist" in exc_info.value.details["allowed_actions"]

    def test_passes_when_shortlist_approved(
        self, 
        initial_state: GraphState,
        sample_applicant: Applicant,
    ):
        """Test that validation passes when shortlist is approved."""
        initial_state.applicants.shortlisted_ids = [str(sample_applicant.id)]
        initial_state.applicants.shortlist_approval = ApprovalStatus.APPROVED
        
        # Should not raise
        validate_state_for_node(initial_state, NodeName.VOICE_PRESCREENING)


# =============================================================================
# Test Validate for SCHEDULE_INTERVIEW
# =============================================================================

class TestValidateForScheduling:
    """Tests for _validate_for_scheduling function."""

    def test_raises_when_prescreening_incomplete(self, initial_state: GraphState):
        """Test that error is raised when prescreening incomplete."""
        initial_state.prescreening.is_complete = False
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_state_for_node(initial_state, NodeName.SCHEDULE_INTERVIEW)
        
        assert NodeName.VOICE_PRESCREENING.value in exc_info.value.details["allowed_actions"]

    def test_raises_when_schedule_not_approved(self, initial_state: GraphState):
        """Test that error is raised when schedule not approved."""
        initial_state.prescreening.is_complete = True
        initial_state.interviews.schedule_approved = False
        
        with pytest.raises(InvalidStateTransitionError) as exc_info:
            validate_state_for_node(initial_state, NodeName.SCHEDULE_INTERVIEW)
        
        assert "approve_schedule" in exc_info.value.details["allowed_actions"]

    def test_passes_when_all_conditions_met(self, initial_state: GraphState):
        """Test that validation passes when all conditions are met."""
        initial_state.prescreening.is_complete = True
        initial_state.interviews.schedule_approved = True
        
        # Should not raise
        validate_state_for_node(initial_state, NodeName.SCHEDULE_INTERVIEW)


# =============================================================================
# Test Nodes Without Validation
# =============================================================================

class TestNodesWithoutValidation:
    """Test that some nodes don't require validation."""

    def test_generate_jd_has_no_validation(self, initial_state: GraphState):
        """Test that GENERATE_JD node has no validation requirements."""
        # Should not raise - GENERATE_JD is not in the validators dict
        validate_state_for_node(initial_state, NodeName.GENERATE_JD)

    def test_review_responses_has_no_validation(self, initial_state: GraphState):
        """Test that REVIEW_RESPONSES node has no validation requirements."""
        # Should not raise
        validate_state_for_node(initial_state, NodeName.REVIEW_RESPONSES)

    def test_reject_candidate_has_no_validation(self, initial_state: GraphState):
        """Test that REJECT_CANDIDATE node has no validation requirements."""
        # Should not raise
        validate_state_for_node(initial_state, NodeName.REJECT_CANDIDATE)
