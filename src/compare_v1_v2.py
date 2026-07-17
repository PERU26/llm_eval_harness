import json


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calc_list_accuracy(score):
    matched = sum(score.get(f, {}).get("matched", 0) for f in ["programming_languages", "tools_and_frameworks", "skills"])
    total = sum(score.get(f, {}).get("total", 0) for f in ["programming_languages", "tools_and_frameworks", "skills"])
    return (matched / total * 100) if total else 0


def summarize(scores, resume_files):
    models = ["gemini", "groq"]
    summary = {}

    for model in models:
        name_correct = years_correct = count = 0
        list_acc_total = 0

        for filename in resume_files:
            s = scores[filename][model]
            if not s.get("parse_success"):
                continue
            count += 1
            name_correct += int(s["name_correct"])
            years_correct += int(s["years_experience_correct"])
            list_acc_total += calc_list_accuracy(s)

        summary[model] = {
            "name_acc_pct": round(name_correct / count * 100, 1) if count else 0,
            "years_acc_pct": round(years_correct / count * 100, 1) if count else 0,
            "list_acc_pct": round(list_acc_total / count, 1) if count else 0
        }

    return summary


def main():
    v1_scores = load_json("results/scores.json")
    v2_scores = load_json("results/scores_v2.json")

    # Only compare on resume_2 and resume_3 - fair comparison,
    # since v2 was only tested on these (resume_1 was the few-shot example)
    resume_files = ["resume_2.txt", "resume_3.txt"]

    v1_summary = summarize(v1_scores, resume_files)
    v2_summary = summarize(v2_scores, resume_files)

    print("A/B TEST: v1 (no example) vs v2 (few-shot example)")
    print("Tested on: resume_2.txt, resume_3.txt only\n")

    print(f"{'Model':<10}{'Version':<10}{'Name%':<8}{'Years%':<8}{'ListAcc%':<10}")
    print("-" * 46)
    for model in ["gemini", "groq"]:
        v1 = v1_summary[model]
        v2 = v2_summary[model]
        print(f"{model:<10}{'v1':<10}{v1['name_acc_pct']:<8}{v1['years_acc_pct']:<8}{v1['list_acc_pct']:<10}")
        print(f"{model:<10}{'v2':<10}{v2['name_acc_pct']:<8}{v2['years_acc_pct']:<8}{v2['list_acc_pct']:<10}")

        diff = round(v2['list_acc_pct'] - v1['list_acc_pct'], 1)
        verdict = "IMPROVED" if diff > 0 else ("WORSE" if diff < 0 else "NO CHANGE")
        print(f"  -> list accuracy change: {diff:+.1f} points ({verdict})\n")


if __name__ == "__main__":
    main()