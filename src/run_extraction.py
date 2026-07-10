import os
import json
import time
from dotenv import load_dotenv
from src.config import PROMPT_TEMPLATE, MODELS

load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from groq import Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_gemini(prompt):
    start = time.time()
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    elapsed = time.time() - start
    return response.text, elapsed


def call_groq(prompt):
    start = time.time()
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    elapsed = time.time() - start
    return completion.choices[0].message.content, elapsed


def main():
    resume_files = ["resume_1.txt", "resume_2.txt", "resume_3.txt"]
    results = {}

    for filename in resume_files:
        with open(f"data/{filename}", "r", encoding="utf-8") as f:
            resume_text = f.read()

        prompt = PROMPT_TEMPLATE.format(resume_text=resume_text)
        results[filename] = {}

        if "gemini" in MODELS:
            print(f"Calling Gemini for {filename}...")
            answer, elapsed = call_gemini(prompt)
            results[filename]["gemini"] = {"raw_answer": answer, "time_seconds": elapsed}

        if "groq" in MODELS:
            print(f"Calling Groq for {filename}...")
            answer, elapsed = call_groq(prompt)
            results[filename]["groq"] = {"raw_answer": answer, "time_seconds": elapsed}

    os.makedirs("results", exist_ok=True)
    with open("results/raw_answers.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\nDone! Saved to results/raw_answers.json")


if __name__ == "__main__":
    main()