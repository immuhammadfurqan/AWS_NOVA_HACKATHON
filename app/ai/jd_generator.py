"""
AARLP JD Generator

Job Description generation supporting multiple AI providers:
- OpenAI GPT-4 (legacy/fallback)
- AWS Bedrock with Nova models (primary for hackathon)

Provider selection is controlled by AI_PROVIDER env var.
"""

import json
from uuid import uuid4

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ai.client import get_openai_client, is_bedrock_provider
from app.jobs.schemas import JobInput, GeneratedJD
from app.ai.prompts import (
    JD_GENERATION_PROMPT,
    PRESCREENING_QUESTIONS_PROMPT,
    JD_REGENERATION_PROMPT,
)

logger = get_logger(__name__)


# ============================================================================
# Provider-Agnostic Generation Functions
# ============================================================================


async def generate_job_description(job_input: JobInput) -> GeneratedJD:
    """
    Generate a job description using the configured AI provider.

    Args:
        job_input: The job requirements from the recruiter

    Returns:
        GeneratedJD: Structured job description
    """
    # Format the prompt with job details
    prompt = JD_GENERATION_PROMPT.format(
        role_title=job_input.role_title,
        department=job_input.department,
        company_name=job_input.company_name,
        company_description=job_input.company_description
        or "A leading company in its field",
        experience_years=job_input.experience_years,
        key_requirements=", ".join(job_input.key_requirements),
        nice_to_have=", ".join(job_input.nice_to_have),
        location=job_input.location or "Flexible",
        salary_range=job_input.salary_range or "Competitive",
    )

    logger.info(
        f"Generating JD for: {job_input.role_title} (provider: {'bedrock' if is_bedrock_provider() else 'openai'})"
    )

    try:
        if is_bedrock_provider():
            result = await _generate_with_bedrock(prompt)
        else:
            result = await _generate_with_openai(prompt)

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
    generated_jd: GeneratedJD, num_questions: int = 5
) -> list[dict]:
    """
    Generate AI-driven prescreening questions based on the JD.

    Args:
        generated_jd: The generated job description
        num_questions: Number of questions to generate

    Returns:
        List of prescreening question dictionaries
    """
    prompt = PRESCREENING_QUESTIONS_PROMPT.format(
        num_questions=num_questions,
        job_title=generated_jd.job_title,
        requirements=", ".join(generated_jd.requirements[:5]),
        responsibilities=(
            ", ".join(generated_jd.responsibilities[:3])
            if generated_jd.responsibilities
            else "N/A"
        ),
    )

    try:
        if is_bedrock_provider():
            result = await _generate_with_bedrock(prompt)
        else:
            result = await _generate_with_openai(prompt)

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
    previous_jd: GeneratedJD, feedback: str
) -> GeneratedJD:
    """
    Regenerate a job description based on recruiter feedback.

    Args:
        previous_jd: The currently generated JD
        feedback: Recruiter's feedback for changes

    Returns:
        GeneratedJD: Newly generated job description
    """
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

    logger.info(
        f"Regenerating JD with feedback: {feedback[:50]}... (provider: {'bedrock' if is_bedrock_provider() else 'openai'})"
    )

    try:
        if is_bedrock_provider():
            result = await _generate_with_bedrock(prompt)
        else:
            result = await _generate_with_openai(prompt)

        jd_data = json.loads(result)
        logger.info("JD regenerated successfully")
        return GeneratedJD(**jd_data)

    except Exception as e:
        logger.exception(f"JD regeneration failed: {e}")
        raise


# ============================================================================
# Provider-Specific Implementations
# ============================================================================

# System prompt for JD generation (ensures proper JSON output)
JD_SYSTEM_PROMPT = (
    "You are an expert HR professional and technical writer. "
    "Always respond with valid JSON matching the requested schema. "
    "Do not include any text outside the JSON object."
)


async def _generate_with_openai(prompt: str) -> str:
    """
    Generate text using OpenAI GPT-4.

    Args:
        prompt: The generation prompt

    Returns:
        Generated text content (JSON string)
    """
    settings = get_settings()
    client = get_openai_client()

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.llm_temperature,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content


async def _generate_with_bedrock(prompt: str) -> str:
    """
    Generate text using AWS Bedrock Nova model.

    Args:
        prompt: The generation prompt

    Returns:
        Generated text content (JSON string)
    """
    from app.ai.bedrock_client import invoke_nova_model

    messages = [{"role": "user", "content": prompt}]

    result = await invoke_nova_model(
        messages=messages,
        system_prompt=JD_SYSTEM_PROMPT,
        max_tokens=4096,
    )

    return _extract_json_from_response(result)


def _extract_json_from_response(result: str) -> str:
    """
    Extract JSON from AI response, handling markdown code blocks.

    This is needed because LLMs sometimes wrap JSON in markdown code blocks
    even when instructed not to.

    Args:
        result: Raw AI response text

    Returns:
        Cleaned JSON string
    """
    if "```json" in result:
        start = result.find("```json") + 7
        end = result.find("```", start)
        if end > start:
            return result[start:end].strip()
    elif "```" in result:
        start = result.find("```") + 3
        end = result.find("```", start)
        if end > start:
            return result[start:end].strip()
    return result
