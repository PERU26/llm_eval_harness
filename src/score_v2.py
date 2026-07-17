import json
from src.score_correctness import clean_json_response, score_one_answer


def main():
    with open("results/raw_answers_v2.json", "r", encoding="utf-8") as f:
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

    with open("results/scores_v2.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)

    print("v2 scoring complete. Saved to results/scores_v2.json")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()