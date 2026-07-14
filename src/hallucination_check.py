import json
import re


def clean_json_response(raw_text):
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    return cleaned.strip()


def check_field_hallucinations(items, resume_text):
    """
    For each item the AI listed, check if it (or a close variant)
    actually appears in the resume text. Returns list of items
    NOT found in the source text - these are potential hallucinations.
    """
    resume_lower = resume_text.lower()
    hallucinated = []

    for item in items:
        item_lower = item.lower().strip()
        # Strip common parenthetical notes, e.g. "NLP (Natural Language Processing)"
        item_core = re.sub(r"\(.*?\)", "", item_lower).strip()

        if item_core not in resume_lower:
            hallucinated.append(item)

    return hallucinated


def check_one_answer(ai_answer, resume_text):
    result = {}

    for field in ["programming_languages", "tools_and_frameworks", "skills"]:
        items = ai_answer.get(field, [])
        hallucinated = check_field_hallucinations(items, resume_text)
        result[field] = {
            "total_claimed": len(items),
            "not_found_in_resume": hallucinated,
            "hallucination_count": len(hallucinated)
        }

    return result


def main():
    with open("results/raw_answers.json", "r", encoding="utf-8") as f:
        raw_answers = json.load(f)

    hallucination_report = {}

    for filename, model_answers in raw_answers.items():
        with open(f"data/{filename}", "r", encoding="utf-8") as f:
            resume_text = f.read()

        hallucination_report[filename] = {}

        for model_name, data in model_answers.items():
            raw_text = data["raw_answer"]
            try:
                cleaned = clean_json_response(raw_text)
                ai_answer = json.loads(cleaned)
                result = check_one_answer(ai_answer, resume_text)
            except json.JSONDecodeError:
                result = {"error": "could not parse JSON"}

            hallucination_report[filename][model_name] = result

    with open("results/hallucination_report.json", "w", encoding="utf-8") as f:
        json.dump(hallucination_report, f, indent=2)

    print("Hallucination check complete. Saved to results/hallucination_report.json")
    print(json.dumps(hallucination_report, indent=2))


if __name__ == "__main__":
    main()