"""
XML Feed Generator for Job Boards

Generates an XML feed compatible with major job boards (Indeed, LinkedIn, Glassdoor).
Format follows the standard referential schema often used for generic XML feeds.
"""

from datetime import datetime
from xml.sax.saxutils import escape

from app.jobs.schemas import GeneratedJD
from app.jobs.models import JobRecord


def generate_xml_feed(
    jobs: list[JobRecord], base_url: str = "https://aarlp.com"
) -> str:
    """
    Generate XML feed string for a list of jobs.

    Args:
        jobs: List of JobRecord objects
        base_url: The base URL of the public career site

    Returns:
        XML string ready for response
    """
    xml_parts = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<source>",
        f'<publisher>{escape("AARLP Recruitment")}</publisher>',
        f"<publisherurl>{escape(base_url)}</publisherurl>",
        f'<lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>',
    ]

    for job in jobs:
        if not job.generated_jd:
            continue

        jd = GeneratedJD.model_validate(job.generated_jd)
        job_url = f"{base_url}/careers/{job.id}"

        # Format date as required (often similar to RSS or specific per board,
        # but ISO dates or standard RSS Dates are usually accepted)
        date_posted = job.created_at.strftime("%Y-%m-%d")

        # Build description with CDATA to preserve HTML
        description = f"<![CDATA[{_build_description_html(jd)}]]>"

        xml_parts.append("<job>")
        xml_parts.append(f"<title>{escape(jd.job_title)}</title>")
        xml_parts.append(f"<date>{escape(date_posted)}</date>")
        xml_parts.append(f"<referencenumber>{escape(str(job.id))}</referencenumber>")
        xml_parts.append(f"<url>{escape(job_url)}</url>")
        xml_parts.append(f"<company>{escape(job.company_name)}</company>")

        if job.company_description:
            xml_parts.append(
                f"<companydescription>{escape(job.company_description)}</companydescription>"
            )

        xml_parts.append(f'<city>{escape(jd.location or "Remote")}</city>')
        xml_parts.append(
            "<country>US</country>"
        )  # Defaulting to US for now, could be dynamic
        xml_parts.append(f"<description>{description}</description>")

        if jd.salary_range:
            xml_parts.append(f"<salary>{escape(jd.salary_range)}</salary>")

        xml_parts.append("</job>")

    xml_parts.append("</source>")
    return "".join(xml_parts)


def _build_description_html(jd: GeneratedJD) -> str:
    """Build simple HTML description from JD sections."""
    parts = [f"<p>{jd.summary}</p>"]

    if jd.description:
        parts.append(f"<p>{jd.description}</p>")

    if jd.responsibilities:
        parts.append("<h3>Responsibilities</h3><ul>")
        for item in jd.responsibilities:
            parts.append(f"<li>{item}</li>")
        parts.append("</ul>")

    if jd.requirements:
        parts.append("<h3>Requirements</h3><ul>")
        for item in jd.requirements:
            parts.append(f"<li>{item}</li>")
        parts.append("</ul>")

    if jd.benefits:
        parts.append("<h3>Benefits</h3><ul>")
        for item in jd.benefits:
            parts.append(f"<li>{item}</li>")
        parts.append("</ul>")

    return "".join(parts)
