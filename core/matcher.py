"""
Transparent, explainable match scoring.

Score Formula (shown in sidebar and results):
  Final Score = 0.70 × Skill Match Score + 0.30 × Semantic Similarity

Component 1 — Skill Match Score (70 % weight)
  Jaccard-style set coverage: |resume_skills ∩ jd_skills| / |jd_skills|
  Rationale: skill presence is binary and highly intentional.

Component 2 — Semantic Similarity (30 % weight)
  TF-IDF cosine similarity between full resume text and JD text.
  Rationale: captures domain vocabulary beyond listed skills
  (e.g. "distributed systems", "fault-tolerant", "cross-functional").

NLP Techniques:
  - TF-IDF (Term Frequency × Inverse Document Frequency) vectorisation
    via sklearn.TfidfVectorizer with unigrams + bigrams (ngram_range=(1,2))
  - Cosine similarity: measures angle between tf-idf vectors;
    immune to document length differences
  - Stop-word removal: sklearn's built-in English stop words
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_WEIGHT = 0.70
SEMANTIC_WEIGHT = 0.30

SCORE_FORMULA = (
    f"Final Score = {int(SKILL_WEIGHT*100)}% × Skill Match "
    f"+ {int(SEMANTIC_WEIGHT*100)}% × Semantic Similarity"
)


def calculate_match_score(
    resume_data: dict,
    jd_data: dict,
    resume_text: str,
    jd_text: str,
) -> dict:
    resume_skills = {s.lower() for s in resume_data.get("skills", [])}
    jd_skills = {s.lower() for s in jd_data.get("skills", [])}

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills

    skill_match_pct = (len(matched) / len(jd_skills) * 100) if jd_skills else 0.0

    semantic_sim = _tfidf_cosine(resume_text, jd_text)

    final_score = SKILL_WEIGHT * skill_match_pct + SEMANTIC_WEIGHT * semantic_sim

    return {
        "final_score": round(final_score, 1),
        "skill_match_pct": round(skill_match_pct, 1),
        "semantic_similarity": round(semantic_sim, 1),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "extra_skills": sorted(extra),
        "jd_skill_count": len(jd_skills),
        "resume_skill_count": len(resume_skills),
        "matched_count": len(matched),
    }


def _tfidf_cosine(text_a: str, text_b: str) -> float:
    """Return cosine similarity (0–100) between two texts using TF-IDF."""
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform([text_a, text_b])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(sim * 100, 2)
    except Exception:
        return 0.0
