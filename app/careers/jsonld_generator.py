"""
JSON-LD Generator for Google for Jobs

Generates schema.org JobPosting structured data from GeneratedJD
for indexing in Google Search results.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel

from app.jobs.schemas import GeneratedJD


class JobPostingJsonLd(BaseModel):
    """JSON-LD output for Google for Jobs."""

    job_id: str
    company_name: str
    jsonld: dict[str, Any]


def generate_job_posting_jsonld(
    job_id: str,
    generated_jd: GeneratedJD,
    company_name: str,
    company_description: str | None = None,
    date_posted: datetime | None = None,
    valid_days: int = 30,
    employment_type: str = "FULL_TIME",
    remote_allowed: bool = False,
) -> JobPostingJsonLd:
    """
    Generate JSON-LD structured data for a job posting.

    Args:
        job_id: Unique identifier for the job
        generated_jd: The AI-generated job description
        company_name: Name of the hiring company
        company_description: Optional company description
        date_posted: When the job was posted (defaults to now)
        valid_days: How many days the posting is valid
        employment_type: FULL_TIME, PART_TIME, CONTRACTOR, INTERN, etc.
        remote_allowed: Whether remote work is allowed

    Returns:
        JobPostingJsonLd with the complete schema.org JobPosting
    """
    if date_posted is None:
        date_posted = datetime.now(timezone.utc)

    valid_through = date_posted + timedelta(days=valid_days)

    # Build the description HTML from JD sections
    description_html = _build_description_html(generated_jd)

    # Parse salary if available
    salary_data = (
        _parse_salary(generated_jd.salary_range) if generated_jd.salary_range else None
    )

    # Build location
    location_data = _build_location(generated_jd.location, remote_allowed)

    jsonld = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": generated_jd.job_title,
        "description": description_html,
        "identifier": {
            "@type": "PropertyValue",
            "name": company_name,
            "value": job_id,
        },
        "datePosted": date_posted.strftime("%Y-%m-%d"),
        "validThrough": valid_through.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "employmentType": employment_type,
        "hiringOrganization": {
            "@type": "Organization",
            "name": company_name,
            "sameAs": None,  # Company website URL if available
        },
    }

    if company_description:
        jsonld["hiringOrganization"]["description"] = company_description

    if location_data:
        jsonld["jobLocation"] = location_data

    if remote_allowed:
        jsonld["jobLocationType"] = "TELECOMMUTE"

    if salary_data:
        jsonld["baseSalary"] = salary_data

    if generated_jd.benefits:
        jsonld["jobBenefits"] = ", ".join(generated_jd.benefits)

    if generated_jd.requirements:
        jsonld["qualifications"] = ", ".join(generated_jd.requirements[:5])

    if generated_jd.responsibilities:
        jsonld["responsibilities"] = ", ".join(generated_jd.responsibilities[:5])

    return JobPostingJsonLd(
        job_id=job_id,
        company_name=company_name,
        jsonld=jsonld,
    )


def _build_description_html(jd: GeneratedJD) -> str:
    """Build HTML description from GeneratedJD sections."""
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

    if jd.nice_to_have:
        parts.append("<h3>Nice to Have</h3><ul>")
        for item in jd.nice_to_have:
            parts.append(f"<li>{item}</li>")
        parts.append("</ul>")

    if jd.benefits:
        parts.append("<h3>Benefits</h3><ul>")
        for item in jd.benefits:
            parts.append(f"<li>{item}</li>")
        parts.append("</ul>")

    return "".join(parts)


def _parse_salary(salary_range: str) -> dict[str, Any] | None:
    """
    Parse salary range string into schema.org MonetaryAmount.

    Handles formats like:
    - "$120,000 - $180,000"
    - "$100k - $150k"
    - "120000-180000"
    """
    import re

    # Remove $ and k suffixes, extract numbers
    cleaned = (
        salary_range.replace("$", "")
        .replace(",", "")
        .replace("k", "000")
        .replace("K", "000")
    )
    numbers = re.findall(r"\d+", cleaned)

    if not numbers:
        return None

    if len(numbers) >= 2:
        min_val = int(numbers[0])
        max_val = int(numbers[1])
        return {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
                "@type": "QuantitativeValue",
                "minValue": min_val,
                "maxValue": max_val,
                "unitText": "YEAR",
            },
        }
    elif len(numbers) == 1:
        return {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
                "@type": "QuantitativeValue",
                "value": int(numbers[0]),
                "unitText": "YEAR",
            },
        }

    return None


def _build_location(location: str | None, remote: bool) -> dict[str, Any] | None:
    """Build schema.org Place from location string."""
    if not location and not remote:
        return None

    if remote or (location and location.lower() == "remote"):
        return {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "US",
            },
        }

    # Parse "City, State" or "City, Country" format
    if location:
        parts = [p.strip() for p in location.split(",")]
        address = {"@type": "PostalAddress"}

        if len(parts) >= 2:
            address["addressLocality"] = parts[0]
            address["addressRegion"] = parts[1]
        else:
            address["addressLocality"] = parts[0]

        return {
            "@type": "Place",
            "address": address,
        }

    return None


def to_script_tag(jsonld: dict[str, Any]) -> str:
    """Convert JSON-LD dict to embeddable script tag."""
    return f'<script type="application/ld+json">{json.dumps(jsonld, indent=2)}</script>'
