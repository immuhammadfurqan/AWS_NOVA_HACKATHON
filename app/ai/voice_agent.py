"""
AARLP Voice Agent Utility

AI-powered voice prescreening using:
- Twilio Voice for phone calls
- ElevenLabs for text-to-speech (alternative)
- OpenAI Whisper for transcription
"""

import asyncio
import base64
import json
import httpx
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone

from twilio.rest import Client as TwilioClient
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.logging import get_logger
from app.candidates.schemas import Applicant, CandidateResponse
from app.interviews.schemas import PrescreeningQuestion
from app.ai.constants import VoiceCallSettings

logger = get_logger(__name__)


# ============================================================================
# Voice Provider Abstraction
# ============================================================================


class VoiceProvider:
    """Base class for voice AI providers."""

    async def initiate_call(
        self,
        phone_number: str,
        questions: list[PrescreeningQuestion],
        candidate_name: str,
        job_title: str,
    ) -> str:
        """Initiate a prescreening call. Returns call ID."""
        raise NotImplementedError

    async def get_call_results(self, call_id: str) -> list[dict]:
        """Get transcribed results for a call."""
        raise NotImplementedError


class TwilioVoiceProvider(VoiceProvider):
    """Twilio-based voice provider."""

    def __init__(self):
        settings = get_settings()
        self.client = TwilioClient(
            settings.twilio_account_sid, settings.twilio_auth_token
        )
        self.from_number = settings.twilio_phone_number

    async def initiate_call(
        self,
        phone_number: str,
        questions: list[PrescreeningQuestion],
        candidate_name: str,
        job_title: str,
    ) -> str:
        """
        Initiate a Twilio voice call.

        In production, this would set up a TwiML webhook for the call flow.
        """
        # Build TwiML for the call
        twiml = self._build_twiml(questions, candidate_name, job_title)

        # Create the call
        loop = asyncio.get_event_loop()
        call = await loop.run_in_executor(
            None,
            lambda: self.client.calls.create(
                to=phone_number,
                from_=self.from_number,
                twiml=twiml,
                record=True,
                recording_status_callback="/webhooks/twilio/recording",
            ),
        )

        return call.sid

    def _build_twiml(
        self,
        questions: list[PrescreeningQuestion],
        candidate_name: str,
        job_title: str,
    ) -> str:
        """Build TwiML for the prescreening call."""
        twiml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            "<Response>",
            f'<Say voice="Polly.Joanna">Hello {candidate_name}. This is an automated prescreening call for the {job_title} position. Please answer the following questions after each beep. You have up to 2 minutes for each response.</Say>',
            '<Pause length="1"/>',
        ]

        for i, question in enumerate(questions, 1):
            twiml_parts.extend(
                [
                    f'<Say voice="Polly.Joanna">Question {i}: {question.question_text}</Say>',
                    '<Pause length="1"/>',
                    "<Play>https://api.twilio.com/cowbell.mp3</Play>",
                    f'<Record maxLength="120" playBeep="false" action="/webhooks/twilio/response/{question.id}"/>',
                    '<Pause length="1"/>',
                ]
            )

        twiml_parts.extend(
            [
                '<Say voice="Polly.Joanna">Thank you for your time. We will review your responses and get back to you soon. Goodbye!</Say>',
                "</Response>",
            ]
        )

        return "\n".join(twiml_parts)

    async def get_call_results(self, call_id: str) -> list[dict]:
        """Get recordings and transcriptions for a call."""
        loop = asyncio.get_event_loop()

        # Fetch recordings
        recordings = await loop.run_in_executor(
            None, lambda: self.client.recordings.list(call_sid=call_id)
        )

        results = []
        for recording in recordings:
            results.append(
                {
                    "recording_sid": recording.sid,
                    "audio_url": f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}",
                    "duration": recording.duration,
                }
            )

        return results


class MockVoiceProvider(VoiceProvider):
    """Mock voice provider for testing."""

    async def initiate_call(
        self,
        phone_number: str,
        questions: list[PrescreeningQuestion],
        candidate_name: str,
        job_title: str,
    ) -> str:
        """Simulate a call."""
        await asyncio.sleep(0.5)  # Simulate network delay
        return f"mock_call_{uuid4().hex[:8]}"

    async def get_call_results(self, call_id: str) -> list[dict]:
        """Return mock results."""
        return [
            {
                "recording_sid": f"mock_rec_{i}",
                "audio_url": f"https://mock.example.com/recordings/{i}.mp3",
                "duration": 45 + i * 10,
                "transcript": f"This is a mock response for question {i}.",
            }
            for i in range(3)
        ]


# ============================================================================
# Transcription
# ============================================================================


async def transcribe_audio(audio_url: str) -> str:
    """
    Transcribe audio using OpenAI Whisper.

    Args:
        audio_url: URL to the audio file

    Returns:
        Transcribed text
    """

    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # Download audio file
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(audio_url)
        audio_data = response.content

    # Transcribe with Whisper
    transcription = await client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.mp3", audio_data, "audio/mpeg"),
    )

    return transcription.text


# ============================================================================
# Scoring
# ============================================================================


async def score_response(
    transcript: str, question: PrescreeningQuestion
) -> tuple[int, str]:
    """
    Score a candidate's response using AI.

    Args:
        transcript: Transcribed response
        question: The question that was asked

    Returns:
        Tuple of (score, rationale)
    """
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    prompt = f"""You are evaluating a candidate's response to a prescreening question.

Question: {question.question_text}

Expected keywords/concepts: {', '.join(question.expected_keywords)}

Candidate's response:
"{transcript}"

Score this response from 0 to {question.max_score} based on:
1. Relevance to the question
2. Depth of answer
3. Use of relevant keywords/concepts
4. Communication clarity

Respond with JSON only:
{{"score": <number>, "rationale": "<brief explanation>"}}
"""

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)

    return result["score"], result["rationale"]


# ============================================================================
# Main Prescreening Function
# ============================================================================


async def conduct_prescreening_calls(
    candidates: list[Applicant],
    questions: list[PrescreeningQuestion],
    use_mock: bool = False,
) -> dict[str, list[CandidateResponse]]:
    """
    Conduct prescreening calls for all candidates.

    Args:
        candidates: List of shortlisted candidates
        questions: Prescreening questions to ask
        use_mock: Use mock provider for testing

    Returns:
        Dictionary mapping candidate_id to their responses
    """
    settings = get_settings()

    # Select provider
    if use_mock:
        provider = MockVoiceProvider()
    elif settings.voice_provider == "twilio":
        provider = TwilioVoiceProvider()
    else:
        # Default to mock for now
        provider = MockVoiceProvider()

    all_responses: dict[str, list[CandidateResponse]] = {}

    for candidate in candidates:
        if not candidate.phone:
            continue

        try:
            responses = await _conduct_single_call(provider, candidate, questions)
            all_responses[str(candidate.id)] = responses

        except Exception as e:
            logger.error(
                "Failed to call candidate",
                extra={"candidate_id": str(candidate.id), "error": str(e)},
            )
            all_responses[str(candidate.id)] = []

    return all_responses


async def _conduct_single_call(
    provider: VoiceProvider,
    candidate: Applicant,
    questions: list[PrescreeningQuestion],
) -> list[CandidateResponse]:
    """Conduct a prescreening call for a single candidate."""

    # Initiate call
    call_id = await provider.initiate_call(
        phone_number=candidate.phone,
        questions=questions,
        candidate_name=candidate.name,
        job_title="the position",  # Would get from state in production
    )

    # Wait for call to complete (in production, this would be webhook-based)
    await asyncio.sleep(VoiceCallSettings.CALL_COMPLETION_WAIT_SECONDS)

    # Get results
    call_results = await provider.get_call_results(call_id)

    responses = []
    for i, (question, result) in enumerate(zip(questions, call_results)):
        # Transcribe if needed
        transcript = result.get("transcript")
        if not transcript and result.get("audio_url"):
            transcript = await transcribe_audio(result["audio_url"])

        # Score the response
        score, rationale = await score_response(transcript or "", question)

        response = CandidateResponse(
            id=uuid4(),
            candidate_id=candidate.id,
            question_id=question.id,
            question_text=question.question_text,
            transcript=transcript or "",
            audio_url=result.get("audio_url"),
            ai_score=score,
            scoring_rationale=rationale,
            call_duration_seconds=result.get("duration"),
            recorded_at=datetime.now(timezone.utc),
        )
        responses.append(response)

    return responses
