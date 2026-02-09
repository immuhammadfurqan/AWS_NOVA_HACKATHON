"""
AARLP AI Prompts

Centralized prompts for all AI operations.
"""

JD_GENERATION_PROMPT = """You are an expert technical recruiter and SEO specialist.
Generate a compelling, SEO-optimized job description based on the following inputs.

# Job Details
- Role Title: {role_title}
- Department: {department}
- Company: {company_name}
- Company Description: {company_description}
- Required Experience: {experience_years} years
- Key Requirements: {key_requirements}
- Nice to Have: {nice_to_have}
- Location: {location}
- Salary Range: {salary_range}

# Instructions
Create a job description that:
1. Has an attention-grabbing, SEO-optimized title
2. Opens with a compelling 2-3 sentence summary
3. Clearly outlines 5-7 key responsibilities
4. Lists requirements in order of importance
5. Highlights unique benefits and company culture
6. Incorporates relevant keywords naturally
7. Uses inclusive language
8. Ends with a clear call-to-action

# Output Format
Return a JSON object with these exact fields:
{{
    "job_title": "string",
    "summary": "string (2-3 sentences)",
    "description": "string (full description)",
    "responsibilities": ["array", "of", "strings"],
    "requirements": ["array", "of", "strings"],
    "nice_to_have": ["array", "of", "strings"],
    "benefits": ["array", "of", "strings"],
    "seo_keywords": ["array", "of", "strings"],
    "salary_range": "string or null",
    "location": "string or null"
}}
"""

PRESCREENING_QUESTIONS_PROMPT = """Based on the following job description, generate {num_questions} 
prescreening questions for a voice-based interview.

Each question should:
1. Be answerable in 1-2 minutes of speaking
2. Assess technical skills or experience relevant to the role
3. Be open-ended to encourage detailed responses
4. Include expected keywords that would indicate a strong answer

# Job Details
- Job Title: {job_title}
- Requirements: {requirements}
- Responsibilities: {responsibilities}

# Output Format
Return a JSON array with objects containing:
[
    {{
        "question_text": "string",
        "expected_keywords": ["array", "of", "5-10", "keywords"],
        "max_score": 100
    }}
]
"""

VOICE_RESPONSE_SCORING_PROMPT = """Score the following candidate response to a prescreening question.

# Question
{question_text}

# Expected Keywords
{expected_keywords}

# Candidate's Response
{transcript}

# Instructions
Evaluate the response based on:
1. Relevance to the question
2. Depth of explanation
3. Use of expected keywords (naturally, not forced)
4. Communication clarity

# Output Format
Return a JSON object:
{{
    "score": <number 0-100>,
    "rationale": "Brief explanation of the score"
}}
"""

JD_REGENERATION_PROMPT = """You are an expert technical recruiter. You previously generated a job description, but the recruiter wants changes.

# Previous Job Description
{previous_jd}

# Recruiter Feedback
{feedback}

# Instructions
Regenerate the job description incorporating the recruiter's feedback. Keep the same structure but apply the requested changes.

# Output Format
Return a JSON object with these exact fields:
{{
    "job_title": "string",
    "summary": "string (2-3 sentences)",
    "description": "string (full description)",
    "responsibilities": ["array", "of", "strings"],
    "requirements": ["array", "of", "strings"],
    "nice_to_have": ["array", "of", "strings"],
    "benefits": ["array", "of", "strings"],
    "seo_keywords": ["array", "of", "strings"],
    "salary_range": "string or null",
    "location": "string or null"
}}

"""

JD_OPTIMIZATION_PROMPT = """You are an expert technical recruiter and SEO strategist.
The previous job description has not attracted enough candidates. Your goal is to optimize it to broaden its appeal without sacrificing quality.

# Current Job Description
{previous_jd}

# Optimization Strategy
1. Relax non-critical requirements (e.g., years of experience, specific nice-to-haves).
2. Emphasize benefits, growth opportunities, and company culture.
3. Improve the hook/summary to be more engaging.
4. Use stronger action verbs.
5. Ensure the language is inclusive and welcoming.

# Instructions
Rewrite the job description to be more attractive to candidates while keeping the core role identity.

# Output Format
Return a JSON object with these exact fields:
{{
    "job_title": "string",
    "summary": "string (2-3 sentences)",
    "description": "string (full description)",
    "responsibilities": ["array", "of", "strings"],
    "requirements": ["array", "of", "strings"],
    "nice_to_have": ["array", "of", "strings"],
    "benefits": ["array", "of", "strings"],
    "seo_keywords": ["array", "of", "strings"],
    "salary_range": "string or null",
    "location": "string or null"
}}
"""
