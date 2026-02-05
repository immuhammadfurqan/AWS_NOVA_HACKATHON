"""
Interviews App Services
"""

from datetime import datetime, timedelta
from typing import Optional, Protocol
from uuid import uuid4

from app.core.config import Settings
from app.core.logging import log_performance, get_logger
from app.core.exceptions import ExternalServiceError
from app.ai.exceptions import TwilioError
from app.interviews.exceptions import GoogleCalendarError

from app.candidates.schemas import Applicant, CandidateResponse
from app.interviews.schemas import PrescreeningQuestion, InterviewSlot, InterviewStatus
from app.interviews.models import InterviewRecord

from app.ai.voice_agent import TwilioVoiceProvider, MockVoiceProvider
from app.interviews.scheduler import get_calendar_service, create_interview_event
from openai import AsyncOpenAI
import json


class VoiceProviderProtocol(Protocol):
    """Protocol for voice provider implementations."""

    async def initiate_call(
        self,
        phone_number: str,
        questions: list[PrescreeningQuestion],
        candidate_name: str,
        job_title: str,
    ) -> str: ...
    async def get_call_results(self, call_id: str) -> list[dict]: ...


class VoiceService:
    """Service layer for voice prescreening operations."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger("VoiceService")
        self._provider: Optional[VoiceProviderProtocol] = None

    @property
    def provider(self) -> VoiceProviderProtocol:
        if self._provider is None:
            self._provider = self._create_provider()
        return self._provider

    def _create_provider(self) -> VoiceProviderProtocol:
        if self.settings.voice_provider == "twilio":
            return TwilioVoiceProvider()
        else:
            return MockVoiceProvider()

    def _log_operation(self, operation: str, success: bool, details: dict = None):
        if details is None:
            details = {}
        status = "success" if success else "failed"
        self.logger.info(f"Operation {operation} {status}", extra=details)

    def _handle_error(self, error: Exception, operation: str, reraise: bool = True):
        self.logger.exception(f"Error in {operation}: {error}")
        if reraise:
            raise error

    @log_performance("voice_service", threshold_ms=30000.0)
    async def conduct_prescreening(
        self,
        candidates: list[Applicant],
        questions: list[PrescreeningQuestion],
        job_title: str = "the position",
    ) -> dict[str, list[CandidateResponse]]:
        """Conduct prescreening calls."""
        self.logger.info(f"Starting prescreening for {len(candidates)} candidates")
        all_responses = {}

        for candidate in candidates:
            if not candidate.phone:
                self.logger.warning(
                    f"Skipping candidate {candidate.id}: no phone number"
                )
                continue
            try:
                responses = await self._conduct_single_call(
                    candidate, questions, job_title
                )
                all_responses[str(candidate.id)] = responses
            except Exception as e:
                self._handle_error(e, "prescreening_call", reraise=False)
                all_responses[str(candidate.id)] = []

        self._log_operation(
            "conduct_prescreening",
            success=True,
            details={"candidates": len(candidates)},
        )
        return all_responses

    async def _conduct_single_call(
        self,
        candidate: Applicant,
        questions: list[PrescreeningQuestion],
        job_title: str,
    ) -> list[CandidateResponse]:
        self.logger.info(f"Calling candidate {candidate.name}")
        call_id = await self.provider.initiate_call(
            phone_number=candidate.phone,
            questions=questions,
            candidate_name=candidate.name,
            job_title=job_title,
        )
        # For production, this should be async result polling or webhook.
        # Here we await results immediately (mock behavior usually).
        call_results = await self.provider.get_call_results(call_id)

        responses = []
        for question, result in zip(questions, call_results):
            transcript = result.get("transcript", "")
            score, rationale = await self._score_response(transcript, question)

            response = CandidateResponse(
                id=uuid4(),
                candidate_id=candidate.id,
                question_id=question.id,
                question_text=question.question_text,
                transcript=transcript,
                audio_url=result.get("audio_url"),
                ai_score=score,
                scoring_rationale=rationale,
                call_duration_seconds=result.get("duration"),
                recorded_at=datetime.utcnow(),
            )
            responses.append(response)
        return responses

    async def _score_response(
        self, transcript: str, question: PrescreeningQuestion
    ) -> tuple[int, str]:
        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        prompt = f"""Evaluate response. Question: {question.question_text}. Keywords: {', '.join(question.expected_keywords)}. Response: "{transcript}". Return JSON: {{"score": <0-{question.max_score}>, "rationale": "..."}}"""
        try:
            response = await client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            return result["score"], result["rationale"]
        except Exception as e:
            self.logger.error(f"Scoring failed: {e}")
            return 0, "Scoring failed"


class CalendarService:
    """Service layer for calendar operations."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger("CalendarService")
        self._service = None

    @property
    def calendar_service(self):
        if self._service is None:
            # Point to new utils location
            try:
                self._service = get_calendar_service()
            except FileNotFoundError:
                self.logger.warning(
                    "Google Calendar credentials not found. Using mock."
                )
                self._service = None
        return self._service

    async def schedule_interview(
        self,
        candidate: Applicant,
        interviewer_email: str,
        scheduled_datetime: datetime,
        job_id: str,
        duration_minutes: int = 60,
        job_title: str = "Technical Interview",
        notes: Optional[str] = None,
    ) -> InterviewSlot:
        self.logger.info(f"Scheduling interview for {candidate.name}")

        if self.calendar_service:
            try:
                return await create_interview_event(
                    candidate=candidate,
                    interviewer_email=interviewer_email,
                    scheduled_datetime=scheduled_datetime,
                    duration_minutes=duration_minutes,
                    job_title=job_title,
                    notes=notes,
                )
            except Exception as e:
                self.logger.warning(f"Calendar event creation failed: {e}")

        # Mock slot
        return InterviewSlot(
            id=uuid4(),
            candidate_id=candidate.id,
            job_id=UUID(job_id) if isinstance(job_id, str) else job_id,
            scheduled_datetime=scheduled_datetime,
            duration_minutes=duration_minutes,
            meeting_link=f"https://meet.google.com/mock-{uuid4().hex[:8]}",
            calendar_event_id=f"mock_event_{uuid4().hex[:8]}",
            interviewer_email=interviewer_email,
            status=InterviewStatus.SCHEDULED,
            notes=notes,
            created_at=datetime.utcnow(),
        )
