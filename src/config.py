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