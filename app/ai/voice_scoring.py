"""
AARLP Voice Response Scoring

AI-powered scoring of candidate voice responses.
"""

import json

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ai.client import get_openai_client
from app.ai.prompts import VOICE_RESPONSE_SCORING_PROMPT
from app.interviews.schemas import PrescreeningQuestion

logger = get_logger(__name__)


async def score_voice_response(
    transcript: str,
    question: PrescreeningQuestion,
) -> tuple[int, str]:
    """
    Score a candidate's voice response using AI.
    
    Args:
        transcript: Transcribed response from the candidate
        question: The prescreening question that was asked
        
    Returns:
        Tuple of (score 0-100, rationale string)
    """
    settings = get_settings()
    client = get_openai_client()
    
    prompt = VOICE_RESPONSE_SCORING_PROMPT.format(
        question_text=question.question_text,
        expected_keywords=", ".join(question.expected_keywords),
        transcript=transcript,
    )
    
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for consistent scoring
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        score = min(100, max(0, int(result.get("score", 50))))
        rationale = result.get("rationale", "No rationale provided")
        
        logger.info(f"Scored response: {score}/100")
        return score, rationale
        
    except Exception as e:
        logger.exception(f"Failed to score response: {e}")
        return 50, "Error during scoring - default score applied"
