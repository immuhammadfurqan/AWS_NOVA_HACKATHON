"""
AARLP Model Tests

Tests for Pydantic models and validation.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from pydantic import ValidationError

from app.models import (
    JobInput,
    GeneratedJD,
    Applicant,
    PrescreeningQuestion,
    CandidateResponse,
    InterviewSlot,
    RecruitmentNodeStatus,
    ApprovalStatus,
    InterviewStatus,
)


class TestJobInput:
    """Tests for JobInput model."""
    
    def test_valid_job_input(self):
        """Test creating a valid job input."""
        job = JobInput(
            role_title="Senior Engineer",
            department="Engineering",
            company_name="TechCorp",
        )
        
        assert job.role_title == "Senior Engineer"
        assert job.department == "Engineering"
        assert job.experience_years == 3  # default
    
    def test_job_input_with_all_fields(self):
        """Test job input with all optional fields."""
        job = JobInput(
            role_title="Senior Engineer",
            department="Engineering",
            company_name="TechCorp",
            company_description="Great company",
            key_requirements=["Python", "FastAPI"],
            nice_to_have=["Docker"],
            experience_years=5,
            location="Remote",
            salary_range="$100k - $150k",
            prescreening_questions=["Tell me about yourself"],
        )
        
        assert len(job.key_requirements) == 2
        assert job.experience_years == 5
    
    def test_job_input_missing_required_fields(self):
        """Test that missing required fields raises error."""
        with pytest.raises(ValidationError):
            JobInput(role_title="Engineer")  # missing department and company
    
    def test_job_input_invalid_experience(self):
        """Test that negative experience is rejected."""
        with pytest.raises(ValidationError):
            JobInput(
                role_title="Engineer",
                department="Eng",
                company_name="Corp",
                experience_years=-1,
            )


class TestGeneratedJD:
    """Tests for GeneratedJD model."""
    
    def test_valid_generated_jd(self, sample_generated_jd: GeneratedJD):
        """Test creating a valid generated JD."""
        assert sample_generated_jd.job_title == "Senior Backend Engineer"
        assert len(sample_generated_jd.responsibilities) > 0
    
    def test_generated_jd_empty_lists(self):
        """Test JD with default empty lists."""
        jd = GeneratedJD(
            job_title="Engineer",
            summary="A role",
            description="Description",
        )
        
        assert jd.responsibilities == []
        assert jd.requirements == []


class TestApplicant:
    """Tests for Applicant model."""
    
    def test_valid_applicant(self):
        """Test creating a valid applicant."""
        applicant = Applicant(
            name="John Doe",
            email="john@example.com",
        )
        
        assert applicant.name == "John Doe"
        assert applicant.id is not None
        assert applicant.shortlisted is False
    
    def test_applicant_with_score(self):
        """Test applicant with similarity score."""
        applicant = Applicant(
            name="Jane Doe",
            email="jane@example.com",
            similarity_score=0.85,
        )
        
        assert applicant.similarity_score == 0.85
    
    def test_applicant_invalid_email(self):
        """Test that invalid email is rejected."""
        with pytest.raises(ValidationError):
            Applicant(
                name="John",
                email="not-an-email",
            )
    
    def test_applicant_score_bounds(self):
        """Test that scores outside 0-1 are rejected."""
        with pytest.raises(ValidationError):
            Applicant(
                name="John",
                email="john@example.com",
                similarity_score=1.5,
            )


class TestPrescreeningQuestion:
    """Tests for PrescreeningQuestion model."""
    
    def test_valid_question(self):
        """Test creating a valid prescreening question."""
        question = PrescreeningQuestion(
            question_text="Tell me about yourself",
            expected_keywords=["experience", "skills"],
        )
        
        assert question.max_score == 100
        assert question.id is not None
    
    def test_question_custom_score(self):
        """Test question with custom max score."""
        question = PrescreeningQuestion(
            question_text="Question",
            max_score=50,
        )
        
        assert question.max_score == 50


class TestCandidateResponse:
    """Tests for CandidateResponse model."""
    
    def test_valid_response(self):
        """Test creating a valid candidate response."""
        response = CandidateResponse(
            candidate_id=uuid4(),
            question_id=uuid4(),
            question_text="Tell me about Python",
            transcript="I have 5 years of Python experience...",
            ai_score=85,
        )
        
        assert response.ai_score == 85
        assert response.recorded_at is not None
    
    def test_response_score_bounds(self):
        """Test that scores outside 0-100 are rejected."""
        with pytest.raises(ValidationError):
            CandidateResponse(
                candidate_id=uuid4(),
                question_id=uuid4(),
                question_text="Question",
                transcript="Answer",
                ai_score=150,
            )


class TestInterviewSlot:
    """Tests for InterviewSlot model."""
    
    def test_valid_interview_slot(self):
        """Test creating a valid interview slot."""
        slot = InterviewSlot(
            candidate_id=uuid4(),
            job_id=uuid4(),
            scheduled_datetime=datetime.utcnow(),
        )
        
        assert slot.status == InterviewStatus.PENDING
        assert slot.duration_minutes == 60
    
    def test_interview_with_meeting_link(self):
        """Test interview with meeting link."""
        slot = InterviewSlot(
            candidate_id=uuid4(),
            job_id=uuid4(),
            scheduled_datetime=datetime.utcnow(),
            meeting_link="https://meet.google.com/abc-defg-hij",
            status=InterviewStatus.SCHEDULED,
        )
        
        assert slot.status == InterviewStatus.SCHEDULED


class TestEnums:
    """Tests for enum models."""
    
    def test_recruitment_node_status_values(self):
        """Test all recruitment node status values."""
        assert RecruitmentNodeStatus.PENDING.value == "pending"
        assert RecruitmentNodeStatus.GENERATE_JD.value == "generate_jd"
        assert RecruitmentNodeStatus.COMPLETED.value == "completed"
    
    def test_approval_status_values(self):
        """Test approval status values."""
        assert ApprovalStatus.PENDING.value == "pending"
        assert ApprovalStatus.APPROVED.value == "approved"
        assert ApprovalStatus.REJECTED.value == "rejected"
    
    def test_interview_status_values(self):
        """Test interview status values."""
        assert InterviewStatus.SCHEDULED.value == "scheduled"
        assert InterviewStatus.COMPLETED.value == "completed"
