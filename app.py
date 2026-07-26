import streamlit as st
import json
import os
import time
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

st.set_page_config(page_title="LLM Evaluation Harness", page_icon="chart", layout="wide")
load_dotenv()

def load_json_safe(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def load_history():
    if not os.path.exists("results/history.db"):
        return pd.DataFrame()
    conn = sqlite3.connect("results/history.db")
    df = pd.read_sql_query("SELECT * FROM run_history ORDER BY timestamp", conn)
    conn.close()
    return df

st.sidebar.title("LLM Evaluation Harness")
st.sidebar.caption("Comparing Gemini vs Groq on structured data extraction")
page = st.sidebar.radio("Go to", ["Overview", "Live Demo"])
st.sidebar.markdown("---")
st.sidebar.markdown("Built as a step-by-step project to measure which AI model is actually more accurate, faster, and less prone to hallucination on a real task.")

if page == "Overview":
    st.title("Model Comparison Overview")
    st.markdown("Comparing Gemini and Groq on extracting structured data from resumes.")
    comparison = load_json_safe("results/comparison_table.json")

    if comparison is None:
        st.warning("No results found yet. Run the pipeline scripts first.")
    else:
        df = pd.DataFrame(comparison)
        df.columns = [c.replace("_", " ").title() for c in df.columns]
        col1, col2 = st.columns(2)
        gemini_row = df[df["Model"] == "gemini"].iloc[0]
        groq_row = df[df["Model"] == "groq"].iloc[0]

        with col1:
            st.subheader("Gemini")
            st.metric("Name Accuracy", str(gemini_row["Name Accuracy Pct"]) + "%")
            st.metric("Years Accuracy", str(gemini_row["Years Experience Accuracy Pct"]) + "%")
            st.metric("List Field Accuracy", str(gemini_row["List Field Accuracy Pct"]) + "%")
            st.metric("Hallucination Rate", str(gemini_row["Hallucination Rate Pct"]) + "%")
            st.metric("Avg Response Time", str(gemini_row["Avg Response Time Sec"]) + "s")

        with col2:
            st.subheader("Groq")
            st.metric("Name Accuracy", str(groq_row["Name Accuracy Pct"]) + "%")
            st.metric("Years Accuracy", str(groq_row["Years Experience Accuracy Pct"]) + "%")
            st.metric("List Field Accuracy", str(groq_row["List Field Accuracy Pct"]) + "%")
            st.metric("Hallucination Rate", str(groq_row["Hallucination Rate Pct"]) + "%")
            st.metric("Avg Response Time", str(groq_row["Avg Response Time Sec"]) + "s")

        st.markdown("---")
        st.subheader("Full comparison table")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Visual comparison")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig = go.Figure(data=[
                go.Bar(name="Gemini", x=["List Accuracy %", "Hallucination %"],
                       y=[gemini_row["List Field Accuracy Pct"], gemini_row["Hallucination Rate Pct"]],
                       marker_color="#4285F4"),
                go.Bar(name="Groq", x=["List Accuracy %", "Hallucination %"],
                       y=[groq_row["List Field Accuracy Pct"], groq_row["Hallucination Rate Pct"]],
                       marker_color="#00A67E"),
            ])
            fig.update_layout(title="Accuracy vs Hallucination Rate", barmode="group", height=350)
            st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            fig2 = go.Figure(data=[
                go.Bar(x=["Gemini", "Groq"],
                       y=[gemini_row["Avg Response Time Sec"], groq_row["Avg Response Time Sec"]],
                       marker_color=["#4285F4", "#00A67E"])
            ])
            fig2.update_layout(title="Average Response Time (seconds)", height=350)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("Key takeaway")
        st.info("Groq is significantly faster (roughly 8x) and flags fewer possible hallucinations. Gemini extracts slightly more complete skill/tool lists but is slower and flags more possible hallucinations - though some of those are arguably reasonable summarization rather than true fabrication.")

    st.markdown("---")
    st.subheader("Results over time")
    history_df = load_history()

    if history_df.empty:
        st.caption("No history yet. Run src/save_history.py to start tracking runs over time.")
    else:
        history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
        avg_by_run = history_df.groupby(["timestamp", "model", "prompt_version"]).agg(
            list_matched=("list_matched", "sum"),
            list_total=("list_total", "sum")
        ).reset_index()
        avg_by_run["list_accuracy_pct"] = (avg_by_run["list_matched"] / avg_by_run["list_total"] * 100).round(1)

        fig3 = go.Figure()
        for model in avg_by_run["model"].unique():
            model_data = avg_by_run[avg_by_run["model"] == model]
            fig3.add_trace(go.Scatter(x=model_data["timestamp"], y=model_data["list_accuracy_pct"], mode="lines+markers", name=model))
        fig3.update_layout(title="List Accuracy % Over Time", height=350, yaxis_title="Accuracy %")
        st.plotly_chart(fig3, use_container_width=True)

        with st.expander("View raw history table"):
            st.dataframe(history_df, use_container_width=True, hide_index=True)

elif page == "Live Demo":
    st.title("Live Demo")
    st.markdown("Paste any resume text below and watch Gemini and Groq extract structured data from it, live.")
    resume_text = st.text_area("Paste resume text here", height=300, placeholder="Paste a resume's text...")

    with st.expander("Optional: provide the correct answer to also see accuracy scoring"):
        st.caption("Fill in the correct values for this resume. Leave all blank to skip accuracy scoring.")

        ans_name = st.text_input("Correct name", placeholder="e.g. Sarah Chen")
        ans_years = st.number_input("Correct years of experience", min_value=0, max_value=60, value=0, step=1)
        ans_languages = st.text_input("Correct programming languages (comma separated)", placeholder="e.g. Python, SQL")
        ans_tools = st.text_input("Correct tools and frameworks (comma separated)", placeholder="e.g. Django, AWS, Docker, Git")
        ans_skills = st.text_input("Correct skills (comma separated)", placeholder="e.g. Machine Learning, Leadership")
        run_button = st.button("Extract with both models", type="primary")
    if run_button:
        if not resume_text.strip():
            st.error("Please paste some resume text first.")
        else:
            from src.config import PROMPT_TEMPLATE
            from src.hallucination_check import check_field_hallucinations
            from src.score_correctness import score_one_answer
            import google.generativeai as genai
            from groq import Groq
            import re
            import json as json_lib
            correct_answer = None
            if ans_name.strip() or ans_years > 0 or ans_languages.strip() or ans_tools.strip() or ans_skills.strip():
                correct_answer = {
                    "name": ans_name.strip(),
                    "years_experience": ans_years,
                    "programming_languages": [x.strip() for x in ans_languages.split(",") if x.strip()],
                    "tools_and_frameworks": [x.strip() for x in ans_tools.split(",") if x.strip()],
                    "skills": [x.strip() for x in ans_skills.split(",") if x.strip()]
                }

            def clean_json_response(raw_text):
                cleaned = raw_text.strip()
                cleaned = re.sub(r"^```json\s*", "", cleaned)
                cleaned = re.sub(r"^```\s*", "", cleaned)
                cleaned = re.sub(r"```\s*$", "", cleaned)
                return cleaned.strip()
            def explain_flag(item, source_text):
                # Check if ANY individual word from the flagged phrase appears in the resume.
                # Some overlap = likely a reasonable summary (e.g. "Leadership" from "led the club").
                # Zero overlap = more likely a true fabrication, not supported by the text at all.
                words = [w.lower() for w in item.split() if len(w) > 3]
                source_lower = source_text.lower()
                overlap = [w for w in words if w in source_lower]

                if overlap:
                    return "likely reasonable summarization (related words found: " + ", ".join(overlap) + ")"
                else:
                    return "likely fabricated (no related words found anywhere in the resume)"

            def show_hallucination_check(parsed_answer, source_text):
                st.markdown("**Hallucination check** (does each claim appear in the resume text?)")
                any_flagged = False
                for field in ["programming_languages", "tools_and_frameworks", "skills"]:
                    items = parsed_answer.get(field, [])
                    flagged = check_field_hallucinations(items, source_text)
                    if flagged:
                        any_flagged = True
                        for item in flagged:
                            reason = explain_flag(item, source_text)
                            st.warning(field + " - \"" + item + "\": " + reason)
                if not any_flagged:
                    st.success("No hallucinations flagged - every claim traces back to the resume text.")
            def show_accuracy_score(parsed_answer, correct_answer):
                if correct_answer is None:
                    return
                score = score_one_answer(parsed_answer, correct_answer)
                st.markdown("**Accuracy vs your answer key**")

                if correct_answer.get("name"):
                    name_icon = "✅" if score["name_correct"] else "❌"
                    st.write(name_icon + " Name correct")

                years_icon = "✅" if score["years_experience_correct"] else "❌"
                st.write(years_icon + " Years experience correct")

                for field in ["programming_languages", "tools_and_frameworks", "skills"]:
                    m = score[field]["matched"]
                    t = score[field]["total"]
                    if t == 0:
                        st.write(field + ": N/A (no correct values provided)")
                    else:
                        pct = round(m / t * 100, 1)
                        st.write(field + ": " + str(m) + "/" + str(t) + " (" + str(pct) + "%)")

            prompt = PROMPT_TEMPLATE.format(resume_text=resume_text)
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Gemini")
                with st.spinner("Calling Gemini..."):
                    try:
                        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                        model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"temperature": 0})
                        start = time.time()
                        response = model.generate_content(prompt)
                        elapsed = time.time() - start
                        cleaned = clean_json_response(response.text)
                        parsed = json.loads(cleaned)
                        st.success("Done in " + str(round(elapsed, 2)) + "s")
                        st.json(parsed)
                        show_hallucination_check(parsed, resume_text)
                        show_accuracy_score(parsed, correct_answer)
                    except Exception as e:
                        st.error("Error: " + str(e))
            with col2:
                st.subheader("Groq")
                with st.spinner("Calling Groq..."):
                    try:
                        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                        start = time.time()
                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0
                        )
                        elapsed = time.time() - start
                        cleaned = clean_json_response(completion.choices[0].message.content)
                        parsed = json.loads(cleaned)
                        st.success("Done in " + str(round(elapsed, 2)) + "s")
                        st.json(parsed)
                        show_hallucination_check(parsed, resume_text)
                        show_accuracy_score(parsed, correct_answer)
                    except Exception as e:
                        st.error("Error: " + str(e))