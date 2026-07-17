"""
Phase 0: Task Definition
This file is the single source of truth for what we're testing.
Every other phase imports from here instead of redefining the task.
"""

# The exact job the AI is being tested on, in one sentence.
TASK_DESCRIPTION = (
    "Given the raw text of a resume, extract the person's name, "
    "years of experience, and skills."
)

# The exact output shape every AI must follow.
OUTPUT_SCHEMA = {
    "name": "string - the person's full name",
    "years_experience": "number - total years of professional experience",
    "programming_languages": "array of strings - languages like Python, Java, SQL",
    "tools_and_frameworks": "array of strings - tools/libraries like Git, TensorFlow, React",
    "skills": "array of strings - concepts/domains like Machine Learning, Communication"
}
PROMPT_TEMPLATE = """You are extracting structured data from a resume.

Return ONLY valid JSON in exactly this shape, nothing else - no explanation, no markdown:
{{
  "name": "string",
  "years_experience": number,
  "programming_languages": ["string", "string", ...],
  "tools_and_frameworks": ["string", "string", ...],
  "skills": ["string", "string", ...]
}}

Rules:
- years_experience: use the number ONLY if the resume explicitly states years of professional work experience. If not explicitly stated, use 0. Do NOT estimate or infer this from project dates, education dates, or anything else.
- programming_languages: only actual programming/query languages (e.g. Python, SQL, JavaScript).
- tools_and_frameworks: only concrete tools, libraries, frameworks, databases, and platforms (e.g. Git, React, PostgreSQL, TensorFlow).
- skills: only broad concepts or domains (e.g. Machine Learning, Communication, Leadership). Do NOT put specific tools or databases here.

Resume text:
{resume_text}
"""# Which models we're comparing.
MODELS = ["gemini", "groq"]

# Phase 7: A/B test - v2 prompt adds a worked example before asking the real question.
# Using resume_1 as the example, so we only test v2 on resume_2 and resume_3
# (testing on resume_1 would be unfair since the model already saw its answer).

FEW_SHOT_EXAMPLE = """Example:

Resume text:
Sarah Chen
Email: sarah.chen@email.com | Phone: (555) 123-4567

SUMMARY
Software engineer with 5 years of experience building backend systems and APIs.

EXPERIENCE
Backend Engineer, TechFlow Inc. (2021 - Present)
- Built REST APIs using Python and Django
- Led migration to microservices architecture

SKILLS
Python, Django, SQL, AWS, Docker, REST APIs, Git

Correct output:
{{
  "name": "Sarah Chen",
  "years_experience": 5,
  "programming_languages": ["Python", "SQL"],
  "tools_and_frameworks": ["Django", "AWS", "Docker", "REST APIs", "Git"],
  "skills": []
}}

Now do the same for this new resume:
"""

PROMPT_TEMPLATE_V2 = """You are extracting structured data from a resume.

Return ONLY valid JSON in exactly this shape, nothing else - no explanation, no markdown:
{{
  "name": "string",
  "years_experience": number,
  "programming_languages": ["string", "string", ...],
  "tools_and_frameworks": ["string", "string", ...],
  "skills": ["string", "string", ...]
}}

Rules:
- years_experience: use the number ONLY if the resume explicitly states years of professional work experience. If not explicitly stated, use 0. Do NOT estimate or infer this from project dates, education dates, or anything else.
- programming_languages: only actual programming/query languages (e.g. Python, SQL, JavaScript).
- tools_and_frameworks: only concrete tools, libraries, frameworks, databases, and platforms (e.g. Git, React, PostgreSQL, TensorFlow).
- skills: only broad concepts or domains (e.g. Machine Learning, Communication, Leadership). Do NOT put specific tools or databases here.
""" + FEW_SHOT_EXAMPLE + """
{resume_text}
"""