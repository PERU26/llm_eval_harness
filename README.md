LLM Evaluation Harness

This is a project I'm building to compare different free LLM APIs (Gemini and Groq) on a real task - extracting structured info from resumes - to see which one performs better in terms of accuracy, hallucinations, speed, and cost using real numbers instead of guesswork.

I'm building this step by step and documenting my progress as I go.

| Model  | Name Acc% | Years Acc% | List Acc% | Hallucination% | Avg Time(s) |
|--------|-----------|------------|-----------|-----------------|------------|
| Gemini | 100.0     | 100.0      | 97.8      | 11.3            | 7.77       |
| Groq   | 100.0     | 100.0      | 93.3      | 4.9             | 0.91       |

Takeaway: Groq is about 8x faster and flags fewer possible hallucinations, but Gemini extracts slightly more complete skill/tool lists. Neither model is a clear "winner" - it depends on whether speed or completeness matters more for the use case. Also worth noting: some of Gemini's higher hallucination rate is arguably reasonable summarization rather than fabrication (see the Phase 4 limitation below), so the real gap may be smaller than the raw number suggests.

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

Phase 4: Hallucination checker
Wrote src/hallucination_check.py to check whether every fact the AI outputs actually appears somewhere in the original resume text. This is a different, broader check than Phase 3 - it catches things the AI might invent even if they weren't part of my answer key at all.

What I found: programming languages and tools/frameworks had zero hallucinations across both models - these tend to be copied fairly literally from the resume. Skills had more flags, especially from Gemini (12 flagged on one resume).

Known limitation: my checker uses exact text matching, so it only catches literal made-up facts. It doesn't understand meaning, so it flags reasonable summarization as a false positive. For example, the resume says "Led The Byte Knights Club... fostering a strong developer community," and the AI summarized this as "Leadership" and "Community Building" - which is a fair, accurate summary, but doesn't appear word-for-word in the resume, so my checker incorrectly flags it as a hallucination.

A more accurate version would need semantic similarity checking (comparing meaning, not just exact words) instead of literal string matching. I'm noting this as a planned improvement rather than fixing it right now, so I can keep moving through the rest of the project - I'll come back to this if time allows.

Phase 5: Comparison table
src/comparison_table.py combines everything from Phases 2-4 into the single results table shown at the top of this README.

Phase 6: Tracking results over time
src/save_history.py saves every scoring run into a local SQLite database (results/history.db), with a timestamp and a label for which prompt version was used. This means every time I improve the prompt or settings, I get a permanent record of whether it actually helped, rather than just overwriting old results and losing that history.

Tech stack
- Python
- Gemini API
- Groq API
- SQLite
  
How to run this
1. Clone the repo
2. pip install python-dotenv google-generativeai groq
3. Add a .env file with your own GEMINI_API_KEY and GROQ_API_KEY
4. Run python -m src.run_extraction
5. Run python -m src.score_correctness
6. Run python -m src.hallucination_check
7. Run python -m src.comparison_table
8. Run python -m src.save_history
