"""SmartResume – AI Resume Analyzer | Streamlit app entry point."""
import os
import streamlit as st
from dotenv import load_dotenv

from core.extractor import extract_text
from core.parser import parse_resume, parse_jd
from core.matcher import calculate_match_score, SCORE_FORMULA
from core.suggestions import rule_based_suggestions, llm_suggestions

load_dotenv()

st.set_page_config(
    page_title="SmartResume – AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")

    st.subheader("Score Formula")
    st.info(SCORE_FORMULA)
    st.caption(
        "**Skill Match (70%):** Fraction of JD skills found in the resume.  \n"
        "**Semantic Similarity (30%):** TF-IDF cosine similarity of resume vs JD text."
    )

    st.divider()

    use_llm = st.toggle("Enable AI Suggestions (Anthropic)", value=False)
    api_key = ""
    if use_llm:
        api_key = st.text_input(
            "Anthropic API Key",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            type="password",
            help="Get your key at console.anthropic.com",
        )

    st.divider()
    st.caption("Built with Python · Streamlit · spaCy · Scikit-learn · Anthropic")

# ── Main layout ───────────────────────────────────────────────────────────────
st.title("📄 SmartResume – AI Resume Analyzer")
st.markdown(
    "Upload a resume and paste a job description to get a **transparent match score**, "
    "skill gap analysis, and actionable improvement suggestions."
)

col_resume, col_jd = st.columns(2)

with col_resume:
    st.subheader("Resume")
    uploaded = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
    resume_text_manual = st.text_area(
        "Or paste resume text here", height=200, key="resume_paste"
    )

with col_jd:
    st.subheader("Job Description")
    jd_text = st.text_area("Paste the full job description", height=300, key="jd_input")

# ── Load sample data helper ───────────────────────────────────────────────────
with st.expander("Load sample data for a quick demo"):
    if st.button("Load Sample Resume + JD"):
        try:
            sample_resume = open("data/sample_resume.txt").read()
            sample_jd = open("data/sample_jd.txt").read()
            st.session_state["resume_paste"] = sample_resume
            st.session_state["jd_input"] = sample_jd
            st.rerun()
        except FileNotFoundError:
            st.warning("Sample files not found. Run the app from the project root.")

# ── Analyse button ────────────────────────────────────────────────────────────
if st.button("🔍 Analyse", type="primary"):
    # Resolve resume text source
    if uploaded:
        with st.spinner("Extracting text from file…"):
            resume_text = extract_text(uploaded, uploaded.name)
    elif resume_text_manual.strip():
        resume_text = resume_text_manual.strip()
    else:
        st.error("Please upload a resume file or paste resume text.")
        st.stop()

    if not jd_text.strip():
        st.error("Please paste a job description.")
        st.stop()

    with st.spinner("Analysing…"):
        resume_data = parse_resume(resume_text)
        jd_data = parse_jd(jd_text)
        match = calculate_match_score(resume_data, jd_data, resume_text, jd_text)

    st.divider()

    # ── Score header ─────────────────────────────────────────────────────────
    score = match["final_score"]
    colour = "🟢" if score >= 65 else "🟡" if score >= 40 else "🔴"
    st.markdown(f"## {colour} Match Score: **{score}/100**")

    c1, c2, c3 = st.columns(3)
    c1.metric("Skill Match", f"{match['skill_match_pct']}%", help="70% weight in final score")
    c2.metric("Semantic Similarity", f"{match['semantic_similarity']}%", help="30% weight in final score")
    c3.metric(
        "Matched Skills",
        f"{match['matched_count']} / {match['jd_skill_count']}",
        help="Skills found in both resume and JD",
    )

    st.progress(int(score))

    st.divider()

    # ── Skill breakdown tabs ──────────────────────────────────────────────────
    tab_match, tab_miss, tab_extra, tab_sections = st.tabs(
        ["✅ Matched Skills", "❌ Missing Skills", "➕ Extra Skills", "📋 Resume Sections"]
    )

    with tab_match:
        if match["matched_skills"]:
            st.success(f"**{len(match['matched_skills'])} skills matched:**")
            st.write(", ".join(f"`{s}`" for s in match["matched_skills"]))
        else:
            st.warning("No skills matched. Check if skill names are spelled consistently.")

    with tab_miss:
        if match["missing_skills"]:
            st.error(f"**{len(match['missing_skills'])} skills in JD not found in resume:**")
            st.write(", ".join(f"`{s}`" for s in match["missing_skills"]))
        else:
            st.success("All JD skills are present in the resume!")

    with tab_extra:
        if match["extra_skills"]:
            st.info(f"**{len(match['extra_skills'])} resume skills not required by this JD:**")
            st.write(", ".join(f"`{s}`" for s in match["extra_skills"]))
        else:
            st.write("No extra skills detected.")

    with tab_sections:
        sections = resume_data.get("sections", {})
        for section, content in sections.items():
            if content:
                with st.expander(section.title()):
                    st.text(content[:600] + ("…" if len(content) > 600 else ""))

    st.divider()

    # ── Suggestions ──────────────────────────────────────────────────────────
    st.subheader("💡 Improvement Suggestions")

    rule_tab, ai_tab = st.tabs(["Rule-based (always available)", "AI Suggestions (optional)"])

    with rule_tab:
        for tip in rule_based_suggestions(match):
            st.markdown(f"- {tip}")

    with ai_tab:
        if use_llm:
            with st.spinner("Generating AI suggestions with claude-opus-5…"):
                ai_advice = llm_suggestions(resume_text, jd_text, match, api_key=api_key)
            st.markdown(ai_advice)
        else:
            st.info("Enable **AI Suggestions** in the sidebar to get richer, contextual advice from Claude.")

    st.divider()

    # ── Raw text expanders ────────────────────────────────────────────────────
    with st.expander("View extracted resume text"):
        st.text(resume_text[:3000])

    with st.expander("Score formula details"):
        st.markdown(
            f"""
**{SCORE_FORMULA}**

| Component | Weight | How it works |
|-----------|--------|--------------|
| Skill Match | 70% | `matched_skills / jd_skills × 100` — exact set overlap |
| Semantic Similarity | 30% | TF-IDF cosine similarity between resume and JD text |

**Why these weights?**
Skills are the primary hiring filter; semantic similarity captures domain vocabulary,
writing style alignment, and soft-keyword overlap that raw skill lists miss.
"""
        )
