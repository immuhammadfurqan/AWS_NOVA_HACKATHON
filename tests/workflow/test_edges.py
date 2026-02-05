"""
Unit Tests for Workflow Edge Functions

Tests the conditional edge functions that determine workflow routing.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.jobs.schemas import JobInput, ApprovalStatus
from app.candidates.schemas import Applicant
from app.workflow.state import GraphState, create_initial_state
from app.workflow.constants import NodeName, WAIT_FOR_HUMAN
from app.workflow.edges import (
    should_regenerate_jd,
    check_jd_approval,
    check_shortlist_approval,
    recruiter_decision,
)


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
def initial_state(sample_job_input: JobInput) -> GraphState:
    """Create initial state for testing."""
    return create_initial_state(sample_job_input)


@pytest.fixture
def sample_applicant() -> Applicant:
    """Create a sample applicant for testing."""
    return Applicant(
        id=uuid4(),
        name="Alice",
        email="alice@test.com",
        resume_text="Python expert",
    )


# =============================================================================
# Test should_regenerate_jd
# =============================================================================

class TestShouldRegenerateJD:
    """Tests for the should_regenerate_jd edge function."""

    def test_returns_wait_when_below_threshold_and_attempts_remaining(
        self, 
        initial_state: GraphState,
    ):
        """Test returns WAIT_FOR_HUMAN when below threshold and can retry."""
        initial_state.applicants.applicants = []  # 0 applicants
        initial_state.applicants.min_threshold = 5
        initial_state.jd.generation_attempts = 1
        
        with patch('app.workflow.edges.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(max_jd_generation_attempts=3)
            
            result = should_regenerate_jd(initial_state)
            
            assert result == WAIT_FOR_HUMAN

    def test_returns_shortlist_when_enough_applicants(
        self, 
        initial_state: GraphState,
        sample_applicant: Applicant,
    ):
        """Test returns SHORTLIST_CANDIDATES when threshold met."""
        initial_state.applicants.applicants = [sample_applicant] * 5  # 5 applicants
        initial_state.applicants.min_threshold = 5
        initial_state.jd.generation_attempts = 1
        
        with patch('app.workflow.edges.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(max_jd_generation_attempts=3)
            
            result = should_regenerate_jd(initial_state)
            
            assert result == NodeName.SHORTLIST_CANDIDATES.value

    def test_returns_shortlist_when_max_attempts_reached(
        self, 
        initial_state: GraphState,
    ):
        """Test returns SHORTLIST_CANDIDATES when max attempts reached."""
        initial_state.applicants.applicants = []  # 0 applicants
        initial_state.applicants.min_threshold = 5
        initial_state.jd.generation_attempts = 3  # Max attempts
        
        with patch('app.workflow.edges.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(max_jd_generation_attempts=3)
            
            result = should_regenerate_jd(initial_state)
            
            assert result == NodeName.SHORTLIST_CANDIDATES.value


# =============================================================================
# Test check_jd_approval
# =============================================================================

class TestCheckJDApproval:
    """Tests for the check_jd_approval edge function."""

    def test_returns_wait_when_pending(self, initial_state: GraphState):
        """Test returns WAIT_FOR_HUMAN when approval is pending."""
        initial_state.jd.approval_status = ApprovalStatus.PENDING
        
        result = check_jd_approval(initial_state)
        
        assert result == WAIT_FOR_HUMAN

    def test_returns_wait_when_rejected(self, initial_state: GraphState):
        """Test returns WAIT_FOR_HUMAN when approval is rejected."""
        initial_state.jd.approval_status = ApprovalStatus.REJECTED
        
        result = check_jd_approval(initial_state)
        
        assert result == WAIT_FOR_HUMAN

    def test_returns_post_job_when_approved(self, initial_state: GraphState):
        """Test returns POST_JOB when approval is approved."""
        initial_state.jd.approval_status = ApprovalStatus.APPROVED
        
        result = check_jd_approval(initial_state)
        
        assert result == NodeName.POST_JOB.value


# =============================================================================
# Test check_shortlist_approval
# =============================================================================

class TestCheckShortlistApproval:
    """Tests for the check_shortlist_approval edge function."""

    def test_returns_wait_when_pending(self, initial_state: GraphState):
        """Test returns WAIT_FOR_HUMAN when approval is pending."""
        initial_state.applicants.shortlist_approval = ApprovalStatus.PENDING
        
        result = check_shortlist_approval(initial_state)
        
        assert result == WAIT_FOR_HUMAN

    def test_returns_wait_when_rejected(self, initial_state: GraphState):
        """Test returns WAIT_FOR_HUMAN when approval is rejected."""
        initial_state.applicants.shortlist_approval = ApprovalStatus.REJECTED
        
        result = check_shortlist_approval(initial_state)
        
        assert result == WAIT_FOR_HUMAN

    def test_returns_voice_prescreening_when_approved(self, initial_state: GraphState):
        """Test returns VOICE_PRESCREENING when approval is approved."""
        initial_state.applicants.shortlist_approval = ApprovalStatus.APPROVED
        
        result = check_shortlist_approval(initial_state)
        
        assert result == NodeName.VOICE_PRESCREENING.value


# =============================================================================
# Test recruiter_decision
# =============================================================================

class TestRecruiterDecision:
    """Tests for the recruiter_decision edge function."""

    def test_returns_schedule_interview_when_approved(self, initial_state: GraphState):
        """Test returns SCHEDULE_INTERVIEW when schedule is approved."""
        initial_state.interviews.schedule_approved = True
        
        result = recruiter_decision(initial_state)
        
        assert result == NodeName.SCHEDULE_INTERVIEW.value

    def test_returns_reject_candidate_when_not_approved(self, initial_state: GraphState):
        """Test returns REJECT_CANDIDATE when schedule is not approved."""
        initial_state.interviews.schedule_approved = False
        
        result = recruiter_decision(initial_state)
        
        assert result == NodeName.REJECT_CANDIDATE.value
