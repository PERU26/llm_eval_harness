import os
import json
import time
from dotenv import load_dotenv
from src.config import PROMPT_TEMPLATE_V2, MODELS

load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from groq import Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_gemini(prompt):
    start = time.time()
    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        generation_config={"temperature": 0}
    )
    response = model.generate_content(prompt)
    elapsed = time.time() - start
    return response.text, elapsed


def call_groq(prompt):
    start = time.time()
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    elapsed = time.time() - start
    return completion.choices[0].message.content, elapsed


def main():
    # Only resume_2 and resume_3 - resume_1 was used as the few-shot example,
    # so testing on it would be unfair (the model already saw its answer).
    resume_files = ["resume_2.txt", "resume_3.txt"]
    results = {}

    for filename in resume_files:
        with open(f"data/{filename}", "r", encoding="utf-8") as f:
            resume_text = f.read()

        prompt = PROMPT_TEMPLATE_V2.format(resume_text=resume_text)
        results[filename] = {}

        if "gemini" in MODELS:
            print(f"Calling Gemini (v2 prompt) for {filename}...")
            answer, elapsed = call_gemini(prompt)
            results[filename]["gemini"] = {"raw_answer": answer, "time_seconds": elapsed}

        if "groq" in MODELS:
            print(f"Calling Groq (v2 prompt) for {filename}...")
            answer, elapsed = call_groq(prompt)
            results[filename]["groq"] = {"raw_answer": answer, "time_seconds": elapsed}

    os.makedirs("results", exist_ok=True)
    with open("results/raw_answers_v2.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\nDone! Saved to results/raw_answers_v2.json")


if __name__ == "__main__":
    main()