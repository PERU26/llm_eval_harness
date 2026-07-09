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
    "skills": "array of strings - technical/professional skills listed"
}

# The instruction we send to every model, every time.
PROMPT_TEMPLATE = """You are extracting structured data from a resume.

Return ONLY valid JSON in exactly this shape, nothing else - no explanation, no markdown:
{{
  "name": "string",
  "years_experience": number,
  "skills": ["string", "string", ...]
}}

Resume text:
{resume_text}
"""

# Which models we're comparing.
MODELS = ["gemini", "groq"]