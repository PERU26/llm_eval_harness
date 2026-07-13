LLM Evaluation Harness

This is a project I'm building to compare different free LLM APIs (Gemini and Groq) on a real task - extracting structured info from resumes - to see which one performs better in terms of accuracy, hallucinations, speed, and cost.

I'm building this step by step and documenting my progress as I go.

Progress

Day 1-2: Setup
Set up the environment, got free API keys for Gemini and Groq, initialized this repo, and made sure secrets (.env) never get pushed to GitHub.

Phase 0: Defining the task
Before writing any real code, I locked down exactly what I'm testing: given a resume's raw text, extract the person's name, years of experience, programming languages, tools/frameworks, and skills, all in a fixed JSON format. This is in src/config.py.

Phase 1: Building an answer key
I collected 3 resumes (2 real ones from classmates, 1 made-up sample) and manually wrote out what the correct extracted data should look like for each. This lives in data/answer_key.json.

Phase 2: Calling the models
Wrote src/run_extraction.py to send each resume to both Gemini and Groq using the same prompt, and save their raw answers along with how long each one took.

Phase 3: Scoring correctness
Wrote src/score_correctness.py to compare each model's answer against my answer key and produce a real accuracy score per resume, per model. Results saved to results/scores.json.

Findings and fixes along the way:
- On my first runs, both models sometimes invented a "years of experience" number on resumes that never stated one (Groq guessed 4, Gemini guessed 1.75, on a student resume with no work history). This is a real hallucination - the model stating something as fact that wasn't actually in the source text.
- I found the models were also non-deterministic - running the exact same resume through the exact same prompt gave different answers each time.
- Gemini kept wrapping its JSON answers in markdown code blocks even though the prompt explicitly said not to. Had to add a cleanup step to strip this before parsing.
- Fix: I set temperature=0 on both models (makes output more consistent/deterministic) and rewrote the prompt to explicitly say "if years of experience isn't stated, use 0, do not estimate from project or education dates." After this fix, both models scored 100% correct on years_experience across all 3 resumes, and tool/framework accuracy also improved.

This before/after is one of the more interesting parts of the project so far - it shows how much prompt design and model settings affect reliability, not just which model you pick.

Next up: Phase 4, building an automated hallucination checker that flags anything the AI mentions that isn't actually in the resume text (separate from just checking known fields against an answer key).

Tech stack
- Python
- Gemini API
- Groq API

How to run this
1. Clone the repo
2. pip install python-dotenv google-generativeai groq
3. Add a .env file with your own GEMINI_API_KEY and GROQ_API_KEY
4. Run python -m src.run_extraction
5. Run python -m src.score_correctness
