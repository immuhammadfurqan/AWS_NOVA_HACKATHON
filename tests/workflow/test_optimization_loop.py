import sys
from unittest.mock import MagicMock

# Mock pinecone before any other imports that might use it
sys.modules["pinecone"] = MagicMock()
sys.modules["pinecone.grpc"] = MagicMock()

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from app.workflow.state import GraphState, create_initial_state
from app.workflow.constants import NodeName
from app.workflow.edges import should_regenerate_jd
from app.workflow.nodes import optimize_jd_node
from app.jobs.schemas import JobInput, GeneratedJD


@pytest.fixture
def sample_job_input() -> JobInput:
    return JobInput(
        role_title="Senior Backend Engineer",
        department="Engineering",
        company_name="TestCorp",
    )


@pytest.fixture
def initial_state(sample_job_input: JobInput) -> GraphState:
    state = create_initial_state(sample_job_input)
    state.jd.generated_jd = GeneratedJD(
        job_title="Engineer",
        summary="Summary",
        description="Desc",
        responsibilities=[],
        requirements=[],
        nice_to_have=[],
        benefits=[],
        seo_keywords=[],
    )
    return state


class TestOptimizationEdge:
    """Test the decision logic in should_regenerate_jd."""

    def test_routes_to_optimize_when_low_candidates(self, initial_state: GraphState):
        """Should return OPTIMIZE_JD when candidates < threshold and attempts < max."""
        initial_state.applicants.applicants = []
        initial_state.applicants.min_threshold = 5
        initial_state.jd.generation_attempts = 1

        with patch("app.workflow.edges.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_jd_generation_attempts=3)

            result = should_regenerate_jd(initial_state)
            assert result == NodeName.OPTIMIZE_JD.value

    def test_routes_to_shortlist_when_max_attempts_reached(
        self, initial_state: GraphState
    ):
        """Should stop optimizing when max attempts reached."""
        initial_state.applicants.applicants = []
        initial_state.jd.generation_attempts = 3

        with patch("app.workflow.edges.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(max_jd_generation_attempts=3)

            result = should_regenerate_jd(initial_state)
            assert result == NodeName.SHORTLIST_CANDIDATES.value


class TestOptimizationNode:
    """Test the optimize_jd_node execution."""

    @pytest.mark.asyncio
    async def test_optimize_node_updates_state(self, initial_state: GraphState):
        """Node should increment attempts, optimize JD, and update timestamp."""
        initial_state.jd.generation_attempts = 1
        initial_state.posting.posted_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Mock the AI function
        mock_optimized_jd = GeneratedJD(
            job_title="Optimized Engineer",
            summary="New Summary",
            description="New Desc",
            responsibilities=[],
            requirements=[],
            nice_to_have=[],
            benefits=[],
            seo_keywords=[],
        )

        with patch(
            "app.workflow.nodes.optimize_job_description", new_callable=AsyncMock
        ) as mock_optimize:
            mock_optimize.return_value = mock_optimized_jd

            # Execute node
            new_state = await optimize_jd_node(initial_state)

            # Verify attempts incremented
            assert new_state.jd.generation_attempts == 2

            # Verify JD updated
            assert new_state.jd.generated_jd.job_title == "Optimized Engineer"

            # Verify posted_at updated (should be newer than old timestamp)
            assert new_state.posting.posted_at > datetime(
                2024, 1, 1, tzinfo=timezone.utc
            )

            # Verify AI called
            mock_optimize.assert_called_once()
