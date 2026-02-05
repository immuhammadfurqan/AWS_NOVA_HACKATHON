"""
AARLP JD Generator

Job Description generation using direct OpenAI calls.
Replaces the slower CrewAI multi-agent approach.
"""

import json
from uuid import uuid4

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ai.client import get_openai_client
from app.jobs.schemas import JobInput, GeneratedJD
from app.ai.prompts import JD_GENERATION_PROMPT, PRESCREENING_QUESTIONS_PROMPT, JD_REGENERATION_PROMPT

logger = get_logger(__name__)


async def generate_job_description(job_input: JobInput) -> GeneratedJD:
    """
    Generate a job description using direct OpenAI call.
    
    This is ~6x faster than the CrewAI approach (~10s vs ~60s).
    
    Args:
        job_input: The job requirements from the recruiter
        
    Returns:
        GeneratedJD: Structured job description
    """
    settings = get_settings()
    client = get_openai_client()
    
    # Format the prompt with job details
    prompt = JD_GENERATION_PROMPT.format(
        role_title=job_input.role_title,
        department=job_input.department,
        company_name=job_input.company_name,
        company_description=job_input.company_description or "A leading company in its field",
        experience_years=job_input.experience_years,
        key_requirements=", ".join(job_input.key_requirements),
        nice_to_have=", ".join(job_input.nice_to_have),
        location=job_input.location or "Flexible",
        salary_range=job_input.salary_range or "Competitive",
    )
    
    logger.info(f"Generating JD for: {job_input.role_title}")
    
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.llm_temperature,
            response_format={"type": "json_object"},
        )
        
        result = response.choices[0].message.content
        jd_data = json.loads(result)
        
        logger.info(f"JD generated successfully for: {job_input.role_title}")
        return GeneratedJD(**jd_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JD response: {e}")
        # Fallback to basic JD
        return GeneratedJD(
            job_title=job_input.role_title,
            summary=f"Join {job_input.company_name} as a {job_input.role_title}.",
            description=f"We are looking for a {job_input.role_title} to join our team.",
            requirements=job_input.key_requirements,
            nice_to_have=job_input.nice_to_have,
            location=job_input.location,
            salary_range=job_input.salary_range,
        )
    except Exception as e:
        logger.exception(f"JD generation failed: {e}")
        raise


async def generate_prescreening_questions(
    generated_jd: GeneratedJD,
    num_questions: int = 5
) -> list[dict]:
    """
    Generate AI-driven prescreening questions based on the JD.
    
    Args:
        generated_jd: The generated job description
        num_questions: Number of questions to generate
        
    Returns:
        List of prescreening question dictionaries
    """
    settings = get_settings()
    client = get_openai_client()
    
    prompt = PRESCREENING_QUESTIONS_PROMPT.format(
        num_questions=num_questions,
        job_title=generated_jd.job_title,
        requirements=", ".join(generated_jd.requirements[:5]),
        responsibilities=", ".join(generated_jd.responsibilities[:3]) if generated_jd.responsibilities else "N/A",
    )
    
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.llm_temperature,
            response_format={"type": "json_object"},
        )
        
        result = response.choices[0].message.content
        
        # Parse the response - it should be a JSON object with a questions array
        data = json.loads(result)
        questions = data.get("questions", data) if isinstance(data, dict) else data
        
        # Add IDs to questions
        for q in questions:
            q["id"] = str(uuid4())
        
        return questions
        
    except Exception as e:
        logger.exception(f"Failed to generate prescreening questions: {e}")
        return []


async def regenerate_job_description(
    previous_jd: GeneratedJD,
    feedback: str
) -> GeneratedJD:
    """
    Regenerate a job description based on recruiter feedback.
    
    Args:
        previous_jd: The currently generated JD
        feedback: Recruiter's feedback for changes
        
    Returns:
        GeneratedJD: Newly generated job description
    """
    settings = get_settings()
    client = get_openai_client()
    
    # Format previous JD as readable text
    previous_jd_text = f"""
Job Title: {previous_jd.job_title}
Summary: {previous_jd.summary}
Description: {previous_jd.description}
Responsibilities: {', '.join(previous_jd.responsibilities)}
Requirements: {', '.join(previous_jd.requirements)}
Nice to Have: {', '.join(previous_jd.nice_to_have)}
Benefits: {', '.join(previous_jd.benefits)}
Location: {previous_jd.location or 'Not specified'}
Salary: {previous_jd.salary_range or 'Not specified'}
"""
    
    prompt = JD_REGENERATION_PROMPT.format(
        previous_jd=previous_jd_text,
        feedback=feedback,
    )
    
    logger.info(f"Regenerating JD with feedback: {feedback[:50]}...")
    
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.llm_temperature,
            response_format={"type": "json_object"},
        )
        
        result = response.choices[0].message.content
        jd_data = json.loads(result)
        
        logger.info("JD regenerated successfully")
        return GeneratedJD(**jd_data)
        
    except Exception as e:
        logger.exception(f"JD regeneration failed: {e}")
        raise
