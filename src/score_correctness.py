import json
import re


def clean_json_response(raw_text):
    """
    Gemini sometimes wraps its answer in markdown code fences like:
```json
    { ... }
```
    This strips that wrapper so we can parse it as plain JSON.
    """
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    return cleaned.strip()


def score_list_field(ai_list, correct_list):
    """
    Compares two lists (e.g. skills) case-insensitively.
    Returns (num_correct, num_expected) so we can compute a percentage later.
    """
    ai_set = set(item.lower().strip() for item in ai_list)
    correct_set = set(item.lower().strip() for item in correct_list)
    matched = ai_set & correct_set
    return len(matched), len(correct_set)


def score_one_answer(ai_answer, correct_answer):
    result = {}

    result["name_correct"] = (
        ai_answer.get("name", "").strip().lower()
        == correct_answer.get("name", "").strip().lower()
    )

    result["years_experience_correct"] = (
        ai_answer.get("years_experience") == correct_answer.get("years_experience")
    )

    for field in ["programming_languages", "tools_and_frameworks", "skills"]:
        matched, total = score_list_field(
            ai_answer.get(field, []), correct_answer.get(field, [])
        )
        result[field] = {"matched": matched, "total": total}

    return result


def main():
    with open("results/raw_answers.json", "r", encoding="utf-8") as f:
        raw_answers = json.load(f)

    with open("data/answer_key.json", "r", encoding="utf-8") as f:
        answer_key = json.load(f)

    scores = {}

    for filename, model_answers in raw_answers.items():
        correct_answer = answer_key[filename]
        scores[filename] = {}

        for model_name, data in model_answers.items():
            raw_text = data["raw_answer"]
            try:
                cleaned = clean_json_response(raw_text)
                ai_answer = json.loads(cleaned)
                score = score_one_answer(ai_answer, correct_answer)
                score["parse_success"] = True
            except json.JSONDecodeError:
                score = {"parse_success": False}

            score["time_seconds"] = data["time_seconds"]
            scores[filename][model_name] = score

    with open("results/scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)

    print("Scoring complete. Saved to results/scores.json")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()