import sqlite3
import json
from datetime import datetime


def init_db():
    """
    Creates the database and table if they don't already exist.
    Safe to run every time - won't wipe existing data.
    """
    conn = sqlite3.connect("results/history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            resume_file TEXT,
            model TEXT,
            name_correct INTEGER,
            years_experience_correct INTEGER,
            list_matched INTEGER,
            list_total INTEGER,
            time_seconds REAL,
            prompt_version TEXT
        )
    """)
    conn.commit()
    return conn


def save_scores_to_db(prompt_version="v1"):
    with open("results/scores.json", "r", encoding="utf-8") as f:
        scores = json.load(f)

    conn = init_db()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()

    for filename, model_data in scores.items():
        for model_name, s in model_data.items():
            if not s.get("parse_success", False):
                continue

            list_matched = sum(
                s.get(field, {}).get("matched", 0)
                for field in ["programming_languages", "tools_and_frameworks", "skills"]
            )
            list_total = sum(
                s.get(field, {}).get("total", 0)
                for field in ["programming_languages", "tools_and_frameworks", "skills"]
            )

            cursor.execute("""
                INSERT INTO run_history
                (timestamp, resume_file, model, name_correct, years_experience_correct,
                 list_matched, list_total, time_seconds, prompt_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                filename,
                model_name,
                int(s.get("name_correct", False)),
                int(s.get("years_experience_correct", False)),
                list_matched,
                list_total,
                s.get("time_seconds", 0),
                prompt_version
            ))

    conn.commit()
    conn.close()
    print(f"Saved {sum(len(m) for m in scores.values())} rows to results/history.db at {timestamp}")


def view_history():
    conn = sqlite3.connect("results/history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, resume_file, model, name_correct, years_experience_correct, list_matched, list_total, time_seconds, prompt_version FROM run_history ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    print(f"\n{'Timestamp':<28}{'Resume':<15}{'Model':<8}{'Name':<6}{'Years':<7}{'List':<10}{'Time(s)':<9}{'PromptVer'}")
    print("-" * 100)
    for row in rows:
        timestamp, resume, model, name_ok, years_ok, matched, total, time_s, prompt_ver = row
        print(f"{timestamp:<28}{resume:<15}{model:<8}{name_ok:<6}{years_ok:<7}{f'{matched}/{total}':<10}{time_s:<9.2f}{prompt_ver}")


if __name__ == "__main__":
    save_scores_to_db(prompt_version="v1")
    view_history()