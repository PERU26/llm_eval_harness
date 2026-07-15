import json


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_comparison():
    scores = load_json("results/scores.json")
    hallucinations = load_json("results/hallucination_report.json")

    models = ["gemini", "groq"]
    summary = {m: {
        "name_correct": 0,
        "years_correct": 0,
        "total_resumes": 0,
        "list_matched": 0,
        "list_total": 0,
        "total_claimed": 0,
        "total_hallucinated": 0,
        "total_time": 0.0,
        "time_count": 0
    } for m in models}

    for filename, model_data in scores.items():
        for model in models:
            s = model_data.get(model, {})
            if not s.get("parse_success", False):
                continue

            row = summary[model]
            row["total_resumes"] += 1
            row["name_correct"] += 1 if s.get("name_correct") else 0
            row["years_correct"] += 1 if s.get("years_experience_correct") else 0
            row["total_time"] += s.get("time_seconds", 0)
            row["time_count"] += 1

            for field in ["programming_languages", "tools_and_frameworks", "skills"]:
                field_data = s.get(field, {})
                row["list_matched"] += field_data.get("matched", 0)
                row["list_total"] += field_data.get("total", 0)

    for filename, model_data in hallucinations.items():
        for model in models:
            h = model_data.get(model, {})
            if "error" in h:
                continue
            row = summary[model]
            for field in ["programming_languages", "tools_and_frameworks", "skills"]:
                field_data = h.get(field, {})
                row["total_claimed"] += field_data.get("total_claimed", 0)
                row["total_hallucinated"] += field_data.get("hallucination_count", 0)

    final_table = []
    for model in models:
        row = summary[model]
        n = row["total_resumes"] or 1
        list_accuracy = (row["list_matched"] / row["list_total"] * 100) if row["list_total"] else 0
        hallucination_rate = (row["total_hallucinated"] / row["total_claimed"] * 100) if row["total_claimed"] else 0
        avg_time = row["total_time"] / row["time_count"] if row["time_count"] else 0

        final_table.append({
            "model": model,
            "name_accuracy_pct": round(row["name_correct"] / n * 100, 1),
            "years_experience_accuracy_pct": round(row["years_correct"] / n * 100, 1),
            "list_field_accuracy_pct": round(list_accuracy, 1),
            "hallucination_rate_pct": round(hallucination_rate, 1),
            "avg_response_time_sec": round(avg_time, 2)
        })

    return final_table


def print_table(table):
    print(f"{'Model':<10}{'Name Acc%':<12}{'Years Acc%':<12}{'List Acc%':<12}{'Halluc%':<10}{'Avg Time(s)':<12}")
    print("-" * 68)
    for row in table:
        print(f"{row['model']:<10}{row['name_accuracy_pct']:<12}{row['years_experience_accuracy_pct']:<12}"
              f"{row['list_field_accuracy_pct']:<12}{row['hallucination_rate_pct']:<10}{row['avg_response_time_sec']:<12}")


def main():
    table = build_comparison()

    with open("results/comparison_table.json", "w", encoding="utf-8") as f:
        json.dump(table, f, indent=2)

    print_table(table)
    print("\nSaved to results/comparison_table.json")


if __name__ == "__main__":
    main()