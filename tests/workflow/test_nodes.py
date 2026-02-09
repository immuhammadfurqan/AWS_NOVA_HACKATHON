"""
Unit Tests for Workflow Node Functions

Tests the individual node functions that power the recruitment workflow.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.jobs.schemas import (
    JobInput,
    GeneratedJD,
    ApprovalStatus,
    RecruitmentNodeStatus,
)
from app.candidates.schemas import Applicant
from app.workflow.state import GraphState, create_initial_state
from app.workflow.constants import NodeName
from app.workflow.exceptions import (
    JDGenerationError,
    ShortlistingError,
    FeatureNotImplementedError,
)
from app.workflow.nodes import (
    generate_jd_node,
    post_job_node,
    shortlist_candidates_node,
    voice_prescreening_node,
    review_responses_node,
    schedule_interview_node,
    reject_candidate_node,
)
from app.workflow.helpers import (
    should_skip_jd_generation,
    prepare_for_jd_generation,
    get_shortlisted_applicants,
    filter_candidates_by_threshold,
    has_prescreening_data,
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
        key_requirements=["Python", "FastAPI"],
        prescreening_questions=["Tell me about Python.", "Describe a bug you fixed."],
    )


@pytest.fixture
def sample_generated_jd() -> GeneratedJD:
    """Create a sample generated JD for testing."""
    return GeneratedJD(
        job_title="Senior Backend Engineer",
        summary="Looking for a great engineer...",
        description="Full description here...",
        responsibilities=["Build APIs", "Review code"],
        requirements=["5+ years Python"],
        nice_to_have=["Kubernetes"],
        benefits=["Remote work"],
        seo_keywords=["python", "backend"],
    )


@pytest.fixture
def initial_state(sample_job_input: JobInput) -> GraphState:
    """Create initial state for testing."""
    return create_initial_state(sample_job_input)


@pytest.fixture
def sample_applicants() -> list[Applicant]:
    """Create sample applicants with similarity scores."""
    return [
        Applicant(
            id=uuid4(),
            name="Alice",
            email="alice@test.com",
            resume_text="Python expert",
            similarity_score=0.85,
        ),
        Applicant(
            id=uuid4(),
            name="Bob",
            email="bob@test.com",
            resume_text="Junior dev",
            similarity_score=0.55,
        ),
        Applicant(
            id=uuid4(),
            name="Carol",
            email="carol@test.com",
            resume_text="FastAPI specialist",
            similarity_score=0.75,
        ),
    ]


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestHelperFunctions:
    """Tests for workflow helper functions."""

    def test_should_skip_jd_generation_false_by_default(
        self, initial_state: GraphState
    ):
        """Test that bypass is False by default."""
        assert should_skip_jd_generation(initial_state) is False

    def test_should_skip_jd_generation_true_when_bypass_set(
        self, initial_state: GraphState
    ):
        """Test that bypass is detected when set."""
        initial_state.jd.bypass_generation = True
        assert should_skip_jd_generation(initial_state) is True

    def test_prepare_for_generation_updates_state(self, initial_state: GraphState):
        """Test that prepare_for_generation updates all required fields."""
        original_attempts = initial_state.jd.generation_attempts

        prepare_for_jd_generation(initial_state)

        assert initial_state.current_node == NodeName.GENERATE_JD.value
        assert initial_state.jd.approval_status == ApprovalStatus.PENDING
        assert initial_state.jd.generation_attempts == original_attempts + 1
        assert initial_state.updated_at is not None

    def test_get_shortlisted_applicants(
        self,
        initial_state: GraphState,
        sample_applicants: list[Applicant],
    ):
        """Test getting shortlisted applicants from state."""
        initial_state.applicants.applicants = sample_applicants
        initial_state.applicants.shortlisted_ids = [
            str(sample_applicants[0].id),
            str(sample_applicants[2].id),
        ]

        shortlisted = get_shortlisted_applicants(initial_state)

        assert len(shortlisted) == 2
        assert sample_applicants[0] in shortlisted
        assert sample_applicants[2] in shortlisted
        assert sample_applicants[1] not in shortlisted

    def test_filter_candidates_by_threshold(self, sample_applicants: list[Applicant]):
        """Test filtering candidates by similarity threshold."""
        # Default threshold is 0.7
        shortlisted_ids = filter_candidates_by_threshold(
            sample_applicants, threshold=0.7
        )

        assert len(shortlisted_ids) == 2  # Alice (0.85) and Carol (0.75)
        assert str(sample_applicants[0].id) in shortlisted_ids  # Alice
        assert str(sample_applicants[2].id) in shortlisted_ids  # Carol
        assert str(sample_applicants[1].id) not in shortlisted_ids  # Bob (0.55)

    def test_has_prescreening_data_false_when_empty(self, initial_state: GraphState):
        """Test has_prescreening_data returns False when no data."""
        assert has_prescreening_data(initial_state) is False

    def test_has_prescreening_data_true_when_data_exists(
        self,
        initial_state: GraphState,
        sample_applicants: list[Applicant],
    ):
        """Test has_prescreening_data returns True when data exists."""
        from app.interviews.schemas import PrescreeningQuestion

        initial_state.applicants.shortlisted_ids = [str(sample_applicants[0].id)]
        initial_state.prescreening.questions = [
            PrescreeningQuestion(
                question_text="Test question",
                expected_keywords=["test"],
                max_score=100,
            )
        ]

        assert has_prescreening_data(initial_state) is True


# =============================================================================
# Node Function Tests
# =============================================================================


class TestGenerateJDNode:
    """Tests for the generate_jd_node function."""

    @pytest.mark.asyncio
    async def test_skips_generation_when_bypass_true(self, initial_state: GraphState):
        """Test that generation is skipped when bypass flag is set."""
        initial_state.jd.bypass_generation = True

        result = await generate_jd_node(initial_state)

        assert result.jd.bypass_generation is False
        assert result.jd.generated_jd is None  # Not generated

    @pytest.mark.asyncio
    async def test_generates_jd_successfully(
        self,
        initial_state: GraphState,
        sample_generated_jd: GeneratedJD,
    ):
        """Test successful JD generation."""
        with patch("app.workflow.nodes.generate_job_description") as mock_gen:
            mock_gen.return_value = sample_generated_jd

            result = await generate_jd_node(initial_state)

            assert result.jd.generated_jd == sample_generated_jd
            assert result.jd.generation_attempts == 1
            assert result.current_node == RecruitmentNodeStatus.JD_REVIEW.value

    @pytest.mark.asyncio
    async def test_initializes_prescreening_questions(
        self,
        initial_state: GraphState,
        sample_generated_jd: GeneratedJD,
    ):
        """Test that prescreening questions are initialized from job input."""
        with patch("app.workflow.nodes.generate_job_description") as mock_gen:
            mock_gen.return_value = sample_generated_jd

            result = await generate_jd_node(initial_state)

            # Questions should be created from job_input.prescreening_questions
            assert len(result.prescreening.questions) == 2

    @pytest.mark.asyncio
    async def test_raises_jd_generation_error_on_failure(
        self, initial_state: GraphState
    ):
        """Test that JDGenerationError is raised on failure."""
        with patch("app.workflow.nodes.generate_job_description") as mock_gen:
            mock_gen.side_effect = Exception("AI service unavailable")

            with pytest.raises(JDGenerationError) as exc_info:
                await generate_jd_node(initial_state)

            assert "AI service unavailable" in str(exc_info.value.details)


class TestPostJobNode:
    """Tests for the post_job_node function."""

    @pytest.mark.asyncio
    async def test_raises_not_implemented_when_disabled(
        self, initial_state: GraphState
    ):
        """Test that FeatureNotImplementedError is raised when feature disabled."""
        with patch("app.workflow.nodes.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(job_posting_enabled=False)

            with pytest.raises(FeatureNotImplementedError) as exc_info:
                await post_job_node(initial_state)

            assert exc_info.value.details["feature_name"] == "job_posting_automation"


class TestShortlistCandidatesNode:
    """Tests for the shortlist_candidates_node function."""

    @pytest.mark.asyncio
    async def test_returns_early_when_no_applicants(
        self,
        initial_state: GraphState,
        sample_generated_jd: GeneratedJD,
    ):
        """Test that node returns early when no applicants."""
        initial_state.jd.generated_jd = sample_generated_jd

        result = await shortlist_candidates_node(initial_state)

        assert result.current_node == NodeName.SHORTLIST_CANDIDATES.value
        assert len(result.applicants.shortlisted_ids) == 0

    @pytest.mark.asyncio
    async def test_raises_error_when_no_jd(
        self,
        initial_state: GraphState,
        sample_applicants: list[Applicant],
    ):
        """Test that error is raised when no JD available."""
        initial_state.applicants.applicants = sample_applicants
        initial_state.jd.generated_jd = None

        with pytest.raises(ShortlistingError) as exc_info:
            await shortlist_candidates_node(initial_state)

        assert "No job description" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_shortlists_candidates_successfully(
        self,
        initial_state: GraphState,
        sample_generated_jd: GeneratedJD,
        sample_applicants: list[Applicant],
    ):
        """Test successful candidate shortlisting."""
        initial_state.jd.generated_jd = sample_generated_jd
        initial_state.applicants.applicants = sample_applicants

        with patch("app.workflow.nodes.rank_candidates_by_similarity") as mock_rank:
            mock_rank.return_value = sample_applicants  # Return with scores already set

            with patch("app.workflow.nodes.get_settings") as mock_settings:
                mock_settings.return_value = MagicMock(
                    shortlist_similarity_threshold=0.7
                )

                result = await shortlist_candidates_node(initial_state)

                # Alice (0.85) and Carol (0.75) should be shortlisted
                assert len(result.applicants.shortlisted_ids) == 2


class TestReviewResponsesNode:
    """Tests for the review_responses_node function."""

    @pytest.mark.asyncio
    async def test_updates_node_and_timestamp(self, initial_state: GraphState):
        """Test that node updates current_node and timestamp."""
        result = await review_responses_node(initial_state)

        assert result.current_node == NodeName.REVIEW_RESPONSES.value
        assert result.updated_at is not None


class TestRejectCandidateNode:
    """Tests for the reject_candidate_node function."""

    @pytest.mark.asyncio
    async def test_updates_node_and_timestamp(self, initial_state: GraphState):
        """Test that node updates current_node and timestamp."""
        result = await reject_candidate_node(initial_state)

        assert result.current_node == NodeName.REJECT_CANDIDATE.value
        assert result.updated_at is not None
