"""
JD Manager service.

Handles job description business logic.
"""

from datetime import datetime, timezone
from uuid import UUID

from app.jobs.schemas import GeneratedJD, RecruitmentNodeStatus, ApprovalStatus
from app.jobs.repository import JobRepository
from app.jobs.exceptions import JDNotGeneratedError
from app.workflow import GraphState
from app.workflow.engine import WorkflowEngine
from app.ai.jd_generator import regenerate_job_description


class JDManager:
    """
    Manages job description operations.

    Single Responsibility: Handle JD business logic.
    """

    def __init__(
        self,
        workflow_engine: WorkflowEngine,
        repository: JobRepository,
        logger,
    ):
        self.workflow_engine = workflow_engine
        self.repository = repository
        self.logger = logger

    async def get_jd(self, state: GraphState) -> GeneratedJD:
        """
        Get generated JD from state.

        Args:
            state: Current graph state

        Returns:
            Generated job description

        Raises:
            JDNotGeneratedError: If JD hasn't been generated yet
        """
        if not state.jd.generated_jd:
            raise JDNotGeneratedError(state.job_id)
        return state.jd.generated_jd

    async def update_jd(
        self, job_id: str, state: GraphState, updates: dict
    ) -> GeneratedJD:
        """
        Update JD fields.

        Args:
            job_id: Job identifier
            state: Current graph state
            updates: Dictionary of fields to update

        Returns:
            Updated job description
        """
        current_jd = await self.get_jd(state)

        # Apply updates to Pydantic model
        for key, value in updates.items():
            if value is not None and hasattr(current_jd, key):
                setattr(current_jd, key, value)

        state.updated_at = datetime.now(timezone.utc)
        await self.workflow_engine.save_state(job_id, state)

        return current_jd

    async def regenerate_jd(
        self, job_id: str, state: GraphState, feedback: str
    ) -> GeneratedJD:
        """
        Regenerate JD with AI using feedback.

        Args:
            job_id: Job identifier
            state: Current graph state
            feedback: Recruiter feedback

        Returns:
            Newly generated job description
        """
        current_jd = await self.get_jd(state)

        # Call AI service
        new_jd = await regenerate_job_description(current_jd, feedback)

        # Update state
        state.jd.generated_jd = new_jd
        state.jd.generation_attempts += 1
        state.updated_at = datetime.now(timezone.utc)
        await self.workflow_engine.save_state(job_id, state)

        return new_jd

    async def approve_jd_state(self, job_id: str, state: GraphState) -> None:
        """
        Update state for JD approval.

        Args:
            job_id: Job identifier
            state: Current graph state
        """
        state.jd.approval_status = ApprovalStatus.APPROVED
        state.current_node = RecruitmentNodeStatus.POST_JOB.value
        state.jd.bypass_generation = True

        # Sync to database for public access (Google for Jobs)
        jd_data = None
        if state.jd.generated_jd:
            jd_data = state.jd.generated_jd.model_dump()

        await self.repository.update(
            UUID(job_id),
            current_node=RecruitmentNodeStatus.POST_JOB.value,
            jd_approval_status=ApprovalStatus.APPROVED.value,
            generated_jd=jd_data,
        )
        await self.workflow_engine.update_and_resume(job_id, state)
