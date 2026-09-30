"""
Two-tier suggestions:
  1. Rule-based (always runs) — deterministic, zero cost, no hallucination risk.
  2. LLM-based (optional) — Anthropic claude-opus-5 for richer, contextual advice.

The two tiers are strictly separated. The LLM never sees candidate skills that
are not already in the resume; it only advises on HOW to address gaps.
"""
import os


def rule_based_suggestions(match_result: dict) -> list[str]:
    suggestions = []
    score = match_result["final_score"]
    missing = match_result["missing_skills"]
    extra = match_result["extra_skills"]
    jd_count = match_result["jd_skill_count"]
    matched = match_result["matched_count"]

    if score < 40:
        suggestions.append(
            "Your profile has significant gaps for this role. "
            "Consider building targeted projects or certifications before applying."
        )
    elif score < 65:
        suggestions.append(
            "Moderate alignment — focus on the missing skills listed below to improve your candidacy."
        )
    else:
        suggestions.append(
            "Strong alignment! Tailor your resume language to mirror the JD wording."
        )

    if missing:
        top_missing = missing[:5]
        suggestions.append(
            f"Priority skill gaps: {', '.join(top_missing)}. "
            "Add these to your resume only after you have genuine hands-on experience."
        )

    if extra and len(extra) > 3:
        suggestions.append(
            f"You have {len(extra)} additional skills not required by this JD. "
            "Trim irrelevant ones to reduce noise and keep recruiters focused."
        )

    if jd_count > 0 and matched / jd_count < 0.5:
        suggestions.append(
            "Less than half the JD skills matched. "
            "Check if skill names in your resume match the exact terms used in the JD (e.g., 'Apache Spark' vs 'Spark')."
        )

    suggestions.append(
        "Quantify your impact: replace vague phrases with metrics "
        "(e.g., 'reduced pipeline latency by 40%', 'processed 10M records/day')."
    )

    return suggestions


def llm_suggestions(
    resume_text: str,
    jd_text: str,
    match_result: dict,
    api_key: str | None = None,
) -> str:
    """Call claude-opus-5 for contextual improvement advice. Returns markdown string."""
    key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return "No Anthropic API key provided. Set ANTHROPIC_API_KEY in .env to enable AI suggestions."

    try:
        import anthropic
    except ImportError:
        return "anthropic package not installed. Run: pip install anthropic"

    missing_str = ", ".join(match_result["missing_skills"][:10]) or "none identified"
    score = match_result["final_score"]

    prompt = f"""You are a professional resume coach. A candidate's resume was compared against a job description.

Match Score: {score}/100
Missing Skills: {missing_str}

RESUME (first 1500 chars):
{resume_text[:1500]}

JOB DESCRIPTION (first 1500 chars):
{jd_text[:1500]}

Provide 4–6 specific, actionable suggestions to improve the resume for this role.
Focus on:
- How to demonstrate missing skills through projects or certifications
- Resume language and phrasing improvements
- Relevant achievements to highlight
- Section-specific improvements

Do NOT fabricate skills or experience the candidate does not have.
Respond in clear markdown bullet points."""

    client = anthropic.Anthropic(api_key=key)
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
