"""
Main Job Service orchestrator.

Coordinates job operations by delegating to specialized helper services.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import RecordNotFoundError
from app.core.logging import get_logger
from app.core.locking import distributed_lock
from app.workflow.exceptions import InvalidStateTransitionError

from app.auth.models import User
from app.jobs.models import JobRecord
from app.jobs.repository import JobRepository
from app.jobs.constants import LockTimeouts, LockKeys, MockDataLimits
from app.jobs.schemas import (
    JobInput,
    JobCreateResponse,
    JobStatusResponse,
    GeneratedJD,
    RecruitmentNodeStatus,
    ApprovalStatus,
    JDApprovalResponse,
    ShortlistApprovalResponse,
    MockApplicantsResponse,
    DeleteJobResponse,
    JobListItem,
    JobListResponse,
)
from app.candidates.schemas import Applicant
from app.workflow import create_initial_state, GraphState
from app.workflow.engine import WorkflowEngine
from app.ai.embeddings import PineconeService

from app.jobs.services.access_control import JobAccessControl
from app.jobs.services.embedding_manager import EmbeddingManager
from app.jobs.services.jd_manager import JDManager
from app.jobs.services.status_builder import StatusBuilder


class JobService:
    """
    Main orchestrator for job operations.

    Delegates to specialized helper services for focused responsibilities.
    This class coordinates high-level workflows.
    """

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        repository: JobRepository,
        workflow_engine: WorkflowEngine,
        pinecone_service: PineconeService,
    ) -> None:
        """Initialize with all dependencies."""
        self.session = session
        self.settings = settings
        self.repository = repository
        self.workflow_engine = workflow_engine
        self.logger = get_logger(__name__)

        # Initialize helper services
        self.access_control = JobAccessControl(repository, self.logger)
        self.embedding_manager = EmbeddingManager(pinecone_service, self.logger)
        self.jd_manager = JDManager(workflow_engine, repository, self.logger)

    def _log_operation(
        self, operation: str, success: bool, details: dict | None = None
    ) -> None:
        """Log operation with structured data."""
        log_data = details or {}
        log_data.update({"operation": operation, "success": success})
        log_method = self.logger.info if success else self.logger.warning
        log_method("Operation completed", extra=log_data)

    async def get_job_state(self, job_id: str) -> GraphState:
        """Get workflow state or raise error."""
        state = await self.workflow_engine.get_state(job_id)
        if not state:
            raise RecordNotFoundError("Job State", job_id)
        return state

    async def create_job(self, job_input: JobInput, user: User) -> JobCreateResponse:
        """
        Create new recruitment job and initialize workflow.

        Args:
            job_input: Job creation parameters
            user: Current user

        Returns:
            Job creation response with ID and status
        """
        self.logger.info("Creating job", extra={"role": job_input.role_title})

        initial_state = create_initial_state(job_input)
        job_id = initial_state.job_id

        job_record = self._create_job_record(job_input, job_id, user)
        await self.repository.create(job_record)
        await self.workflow_engine.invoke(initial_state, job_id)

        self._log_operation(
            "create_job",
            success=True,
            details={"job_id": job_id, "role": job_input.role_title},
        )

        return JobCreateResponse(
            job_id=UUID(job_id),
            thread_id=job_id,
            message="Recruitment process started. JD generation in progress.",
            current_node=RecruitmentNodeStatus.GENERATE_JD,
        )

    def _create_job_record(
        self, job_input: JobInput, job_id: str, user: User
    ) -> JobRecord:
        """Create JobRecord instance."""
        now = datetime.now(timezone.utc)
        return JobRecord(
            id=UUID(job_id),
            thread_id=job_id,
            role_title=job_input.role_title,
            company_name=job_input.company_name,
            company_description=job_input.company_description,
            current_node=RecruitmentNodeStatus.GENERATE_JD.value,
            jd_approval_status="pending",
            created_at=now,
            updated_at=now,
            owner_id=user.id,
        )

    async def get_job_status(self, job_id: str, user: User) -> JobStatusResponse:
        """Get formatted job status."""
        job_record = await self.access_control.ensure_access(job_id, user)

        try:
            state = await self.get_job_state(job_id)
            return StatusBuilder.from_state(state)
        except RecordNotFoundError:
            return StatusBuilder.from_record(job_record)

    async def get_generated_jd(self, job_id: str, user: User) -> GeneratedJD:
        """Get generated job description."""
        await self.access_control.ensure_access(job_id, user)
        state = await self.get_job_state(job_id)
        return await self.jd_manager.get_jd(state)

    async def approve_jd(self, job_id: str, user: User) -> JDApprovalResponse:
        """Approve generated JD with distributed locking."""
        await self.access_control.ensure_access(job_id, user)

        try:
            async with distributed_lock(
                LockKeys.job_approval(job_id), timeout=LockTimeouts.JOB_APPROVAL
            ):
                state = await self.get_job_state(job_id)
                await self.jd_manager.approve_jd_state(job_id, state)
                await self.embedding_manager.store_jd_embedding(
                    job_id, state.jd.generated_jd
                )

            self._log_operation("approve_jd", success=True, details={"job_id": job_id})
            return JDApprovalResponse(
                message="JD approved. Job posting initiated.",
                job_id=job_id,
            )
        except Exception as e:
            self.logger.exception("Error approving JD", extra={"job_id": job_id})
            raise

    async def update_jd(self, job_id: str, jd_update: dict, user: User) -> GeneratedJD:
        """Manually update JD fields."""
        await self.access_control.ensure_access(job_id, user)
        state = await self.get_job_state(job_id)
        updated_jd = await self.jd_manager.update_jd(job_id, state, jd_update)

        self._log_operation("update_jd", success=True, details={"job_id": job_id})
        return updated_jd

    async def regenerate_jd(
        self, job_id: str, feedback: str, user: User
    ) -> GeneratedJD:
        """Regenerate JD using AI with feedback."""
        await self.access_control.ensure_access(job_id, user)
        state = await self.get_job_state(job_id)
        new_jd = await self.jd_manager.regenerate_jd(job_id, state, feedback)

        self._log_operation(
            "regenerate_jd",
            success=True,
            details={"job_id": job_id, "feedback": feedback[:50]},
        )
        return new_jd

    async def approve_shortlist(
        self, job_id: str, user: User
    ) -> ShortlistApprovalResponse:
        """Approve shortlisted candidates."""
        await self.access_control.ensure_access(job_id, user)

        async with distributed_lock(
            LockKeys.shortlist_approval(job_id),
            timeout=LockTimeouts.SHORTLIST_APPROVAL,
        ):
            state = await self.get_job_state(job_id)
            self._validate_shortlist_state(state)
            self._update_shortlist_state(state)
            await self.workflow_engine.save_state(job_id, state)

        self._log_operation(
            "approve_shortlist", success=True, details={"job_id": job_id}
        )

        return ShortlistApprovalResponse(
            message="Shortlist approved. Voice prescreening will begin.",
            shortlisted_count=len(state.applicants.shortlisted_ids),
        )

    def _validate_shortlist_state(self, state: GraphState) -> None:
        """Validate state allows shortlist approval."""
        if state.current_node != RecruitmentNodeStatus.SHORTLIST_CANDIDATES.value:
            raise InvalidStateTransitionError(
                current_node=state.current_node,
                attempted_action="approve_shortlist",
                allowed_actions=["wait for shortlist_candidates state"],
            )

    def _update_shortlist_state(self, state: GraphState) -> None:
        """Update state for shortlist approval."""
        state.applicants.shortlist_approval = ApprovalStatus.APPROVED
        state.updated_at = datetime.now(timezone.utc)

    async def execute_graph_background(self, job_id: str, state: GraphState) -> None:
        """Execute recruitment graph in background with locking."""
        try:
            async with distributed_lock(
                LockKeys.job_graph(job_id),
                timeout=LockTimeouts.JOB_GRAPH_EXECUTION,
            ):
                await self.workflow_engine.invoke(state, job_id)

            self._log_operation(
                "execute_graph", success=True, details={"job_id": job_id}
            )
        except Exception as e:
            self.logger.exception("Error executing graph", extra={"job_id": job_id})
            await self._save_error_state(job_id, state, str(e))

    async def _save_error_state(
        self, job_id: str, state: GraphState, error: str
    ) -> None:
        """Save error message to state (best effort)."""
        try:
            state.error_message = error
            await self.workflow_engine.save_state(job_id, state)
        except Exception:
            pass  # Don't raise on error save failure

    async def add_mock_applicants(
        self, job_id: str, user: User, count: int = MockDataLimits.DEFAULT_APPLICANTS
    ) -> MockApplicantsResponse:
        """Add mock applicants for testing."""
        await self.access_control.ensure_access(job_id, user)

        count = self._clamp_applicant_count(count)
        state = await self.get_job_state(job_id)

        for i in range(count):
            applicant = self._create_mock_applicant(i)
            state.applicants.applicants.append(applicant)

        state.applicants.monitoring_complete = True
        state.updated_at = datetime.now(timezone.utc)
        await self.workflow_engine.save_state(job_id, state)

        return MockApplicantsResponse(
            message=f"Added {count} mock applicants",
            total_applicants=len(state.applicants.applicants),
        )

    def _clamp_applicant_count(self, count: int) -> int:
        """Ensure count is within valid bounds."""
        return max(
            MockDataLimits.MIN_APPLICANTS,
            min(count, MockDataLimits.MAX_APPLICANTS),
        )

    def _create_mock_applicant(self, index: int) -> Applicant:
        """Create a single mock applicant."""
        return Applicant(
            id=uuid4(),
            name=f"Test Candidate {index + 1}",
            email=f"candidate{index + 1}@example.com",
            phone=f"+1555000000{index}",
            resume_path=None,
            resume_text=(
                f"Experienced developer with {3 + index} years of experience "
                "in Python, FastAPI, and PostgreSQL."
            ),
            embedding=None,
            similarity_score=None,
            shortlisted=False,
        )

    async def delete_job(self, job_id: str, user: User) -> DeleteJobResponse:
        """Delete job and all associated data."""
        await self.access_control.ensure_access(job_id, user)

        # Delete embeddings (best effort)
        await self.embedding_manager.delete_job_embeddings(job_id)

        # Delete from database
        rowcount = await self.repository.delete(UUID(job_id))
        if rowcount == 0:
            raise RecordNotFoundError("Job", job_id)

        self._log_operation("delete_job", success=True, details={"job_id": job_id})
        return DeleteJobResponse(message=f"Job {job_id} deleted successfully")

    async def list_jobs(self, user: User) -> JobListResponse:
        """
        List all jobs for the current user.

        Args:
            user: Current authenticated user

        Returns:
            JobListResponse with list of user's jobs
        """
        jobs = await self.repository.get_by_user_id(user.id)

        job_items = [
            JobListItem(
                job_id=job.id,
                role_title=job.role_title,
                company_name=job.company_name,
                current_node=RecruitmentNodeStatus(job.current_node),
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
            for job in jobs
        ]

        self._log_operation(
            "list_jobs",
            success=True,
            details={"user_id": str(user.id), "count": len(job_items)},
        )
        return JobListResponse(jobs=job_items, total=len(job_items))
