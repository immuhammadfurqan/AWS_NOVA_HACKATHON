"""
AARLP PDF Parser Utility

Extracts text content from PDF resumes for embedding and analysis.
"""

import asyncio
from pathlib import Path
from typing import Optional

import pdfplumber

from app.core.logging import get_logger

logger = get_logger(__name__)


async def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text content from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text content or None if extraction fails
    """
    try:
        path = Path(pdf_path)
        if not path.exists():
            return None

        # Run PDF extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, _extract_sync, str(path))

        return text

    except Exception as e:
        logger.error(
            "PDF extraction failed",
            extra={"path": pdf_path, "error": str(e)},
        )
        return None


def _extract_sync(pdf_path: str) -> str:
    """Synchronous PDF text extraction."""
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


async def extract_text_from_multiple_pdfs(
    pdf_paths: list[str],
) -> dict[str, Optional[str]]:
    """
    Extract text from multiple PDF files concurrently.

    Args:
        pdf_paths: List of paths to PDF files

    Returns:
        Dictionary mapping file paths to extracted text
    """
    tasks = [extract_text_from_pdf(path) for path in pdf_paths]
    results = await asyncio.gather(*tasks)

    return dict(zip(pdf_paths, results))


def clean_resume_text(text: str) -> str:
    """
    Clean and normalize extracted resume text.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove excessive whitespace
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    # Join with single newlines
    cleaned = "\n".join(cleaned_lines)

    # Remove very long lines (likely parsing errors)
    max_line_length = 500
    final_lines = []
    for line in cleaned.split("\n"):
        if len(line) <= max_line_length:
            final_lines.append(line)

    return "\n".join(final_lines)
