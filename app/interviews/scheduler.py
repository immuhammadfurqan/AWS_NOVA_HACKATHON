"""
AARLP Interview Scheduler Utility

Google Calendar integration for:
- Checking interviewer availability
- Creating interview events with Meet links
- Sending calendar invites
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4
import os
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.core.config import get_settings
from app.candidates.schemas import Applicant
from app.interviews.schemas import InterviewSlot, InterviewStatus


# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


# ============================================================================
# Google Calendar Authentication
# ============================================================================

def get_calendar_credentials() -> Credentials:
    """
    Get or refresh Google Calendar credentials.
    
    Uses OAuth2 flow for first-time authorization.
    """
    settings = get_settings()
    creds = None
    
    # Load existing token
    if os.path.exists(settings.google_calendar_token_file):
        with open(settings.google_calendar_token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(settings.google_calendar_credentials_file):
                raise FileNotFoundError(
                    f"Google Calendar credentials file not found: "
                    f"{settings.google_calendar_credentials_file}"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.google_calendar_credentials_file,
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(settings.google_calendar_token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def get_calendar_service():
    """Get Google Calendar API service."""
    creds = get_calendar_credentials()
    return build('calendar', 'v3', credentials=creds)


# ============================================================================
# Availability Checking
# ============================================================================

async def get_available_slots(
    interviewer_email: str,
    date_range_start: datetime,
    date_range_end: datetime,
    duration_minutes: int = 60,
    working_hours: tuple[int, int] = (9, 17),
) -> list[datetime]:
    """
    Find available interview slots for an interviewer.
    
    Args:
        interviewer_email: Email of the interviewer
        date_range_start: Start of date range to search
        date_range_end: End of date range to search
        duration_minutes: Required duration for interview
        working_hours: Tuple of (start_hour, end_hour) in 24h format
        
    Returns:
        List of available datetime slots
    """
    loop = asyncio.get_event_loop()
    
    def _get_busy_times():
        service = get_calendar_service()
        
        body = {
            "timeMin": date_range_start.isoformat() + "Z",
            "timeMax": date_range_end.isoformat() + "Z",
            "items": [{"id": interviewer_email}],
        }
        
        result = service.freebusy().query(body=body).execute()
        
        busy_times = []
        for busy in result["calendars"].get(interviewer_email, {}).get("busy", []):
            start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))
            busy_times.append((start, end))
        
        return busy_times
    
    busy_times = await loop.run_in_executor(None, _get_busy_times)
    
    # Generate available slots
    available_slots = []
    current = date_range_start.replace(minute=0, second=0, microsecond=0)
    
    while current < date_range_end:
        # Check if within working hours
        if working_hours[0] <= current.hour < working_hours[1]:
            slot_end = current + timedelta(minutes=duration_minutes)
            
            # Check if slot conflicts with any busy time
            is_available = True
            for busy_start, busy_end in busy_times:
                if current < busy_end and slot_end > busy_start:
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(current)
        
        # Move to next slot (30-minute increments)
        current += timedelta(minutes=30)
    
    return available_slots


# ============================================================================
# Event Creation
# ============================================================================

async def create_interview_event(
    candidate: Applicant,
    interviewer_email: str,
    scheduled_datetime: datetime,
    duration_minutes: int = 60,
    job_title: str = "Technical Interview",
    notes: Optional[str] = None,
) -> InterviewSlot:
    """
    Create a Google Calendar event for an interview.
    
    Args:
        candidate: The candidate being interviewed
        interviewer_email: Email of the interviewer
        scheduled_datetime: When to schedule the interview
        duration_minutes: Duration of the interview
        job_title: Title/role being interviewed for
        notes: Optional notes for the interview
        
    Returns:
        InterviewSlot with calendar event details
    """
    loop = asyncio.get_event_loop()
    
    def _create_event():
        service = get_calendar_service()
        
        end_time = scheduled_datetime + timedelta(minutes=duration_minutes)
        
        event = {
            'summary': f"Interview: {candidate.name} - {job_title}",
            'description': f"""
Technical Interview for {job_title}

Candidate: {candidate.name}
Email: {candidate.email}
Phone: {candidate.phone or 'N/A'}

{notes or ''}
            """.strip(),
            'start': {
                'dateTime': scheduled_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': interviewer_email},
                {'email': candidate.email},
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid4()),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                },
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1,
            sendUpdates='all',
        ).execute()
        
        return created_event
    
    event = await loop.run_in_executor(None, _create_event)
    
    # Extract meeting link
    meeting_link = None
    if 'conferenceData' in event:
        entry_points = event['conferenceData'].get('entryPoints', [])
        for ep in entry_points:
            if ep.get('entryPointType') == 'video':
                meeting_link = ep.get('uri')
                break
    
    return InterviewSlot(
        id=uuid4(),
        candidate_id=candidate.id,
        job_id=uuid4(),  # Would be passed in production
        scheduled_datetime=scheduled_datetime,
        duration_minutes=duration_minutes,
        meeting_link=meeting_link,
        calendar_event_id=event.get('id'),
        interviewer_email=interviewer_email,
        status=InterviewStatus.SCHEDULED,
        notes=notes,
        created_at=datetime.utcnow(),
    )


# ============================================================================
# Batch Scheduling
# ============================================================================

async def schedule_interviews(
    job_id: str,
    candidates: list[Applicant],
    interviewer_email: Optional[str] = None,
    start_date: Optional[datetime] = None,
    duration_minutes: int = 60,
) -> list[InterviewSlot]:
    """
    Schedule interviews for multiple candidates.
    
    Automatically finds available slots and creates calendar events.
    
    Args:
        job_id: ID of the job
        candidates: List of candidates to schedule
        interviewer_email: Email of interviewer (uses settings default if not provided)
        start_date: Start date for scheduling (defaults to tomorrow)
        duration_minutes: Duration for each interview
        
    Returns:
        List of scheduled InterviewSlot objects
    """
    if not interviewer_email:
        # Would get from job configuration in production
        raise ValueError("Interviewer email is required")
    
    if not start_date:
        start_date = datetime.utcnow() + timedelta(days=1)
        start_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    end_date = start_date + timedelta(days=14)  # Look 2 weeks ahead
    
    # Get available slots
    available_slots = await get_available_slots(
        interviewer_email=interviewer_email,
        date_range_start=start_date,
        date_range_end=end_date,
        duration_minutes=duration_minutes,
    )
    
    if len(available_slots) < len(candidates):
        print(f"Warning: Only {len(available_slots)} slots available for {len(candidates)} candidates")
    
    scheduled = []
    for candidate, slot in zip(candidates, available_slots):
        try:
            interview = await create_interview_event(
                candidate=candidate,
                interviewer_email=interviewer_email,
                scheduled_datetime=slot,
                duration_minutes=duration_minutes,
            )
            scheduled.append(interview)
        except Exception as e:
            print(f"Error scheduling interview for {candidate.name}: {e}")
    
    return scheduled


# ============================================================================
# Mock Scheduler for Testing
# ============================================================================

async def mock_schedule_interviews(
    job_id: str,
    candidates: list[Applicant],
) -> list[InterviewSlot]:
    """
    Mock interview scheduling for testing without Google Calendar.
    """
    scheduled = []
    base_time = datetime.utcnow() + timedelta(days=1)
    
    for i, candidate in enumerate(candidates):
        slot_time = base_time + timedelta(hours=i * 2)
        
        interview = InterviewSlot(
            id=uuid4(),
            candidate_id=candidate.id,
            job_id=UUID(job_id) if isinstance(job_id, str) else job_id,
            scheduled_datetime=slot_time,
            duration_minutes=60,
            meeting_link=f"https://meet.google.com/mock-{uuid4().hex[:8]}",
            calendar_event_id=f"mock_event_{uuid4().hex[:8]}",
            interviewer_email="interviewer@example.com",
            status=InterviewStatus.SCHEDULED,
            created_at=datetime.utcnow(),
        )
        scheduled.append(interview)
    
    return scheduled
