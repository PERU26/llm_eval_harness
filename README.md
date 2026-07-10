# LLM Evaluation Harness

This is a project I'm building to compare different free LLM APIs (Gemini and Groq) on a real task - extracting structured info from resumes - to see which one performs better in terms of accuracy, hallucinations, speed, and cost.

I'm building this step by step and documenting my progress as I go.

## Progress

### Day 1-2: Setup

Set up the environment, got free API keys for Gemini and Groq, initialized this repo, and made sure secrets (.env) never get pushed to GitHub.

### Phase 0: Defining the task

Before writing any real code, I locked down exactly what I'm testing: given a resume's raw text, extract the person's name, years of experience, programming languages, tools/frameworks, and skills, all in a fixed JSON format. This is in src/config.py.

### Phase 1: Building an answer key

I collected 3 resumes (2 real ones from classmates, 1 made-up sample) and manually wrote out what the correct extracted data should look like for each. This lives in data/answer\_key.json.

### Phase 2: Calling the models

Wrote src/run\_extraction.py to send each resume to both Gemini and Groq using the same prompt, and save their raw answers along with how long each one took.

Some things I noticed right away:

* Groq is way faster than Gemini, about 10-20x faster per call
* Groq made up a "4 years of experience" value on a resume that never mentioned any work experience at all. Gemini got this one right and said 0. Good example of the hallucination problem this project is trying to measure.
* Gemini kept wrapping its JSON answers in markdown code blocks even though I told it not to in the prompt. Groq didn't do this. Have to clean that up before parsing both the same way.

Next up: Phase 3, writing the scoring logic to compare AI answers against my answer key and get real accuracy numbers.

## Tech stack

* Python
* Gemini API
* Groq API

## How to run this

1. Clone the repo
2. pip install python-dotenv google-generativeai groq
3. Add a .env file with your own GEMINI\_API\_KEY and GROQ\_API\_KEY
4. Run python -m src.run\_extraction

