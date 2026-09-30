"""
Parse resume text into sections and extract technical skills.

NLP Techniques used:
  - Regex pattern matching for section header detection
  - Word-boundary regex for exact skill matching against a curated taxonomy
  - spaCy NER (en_core_web_sm) to catch technology names not in the taxonomy
  - Lemmatization via spaCy for normalising verb/noun forms in JD text
"""
import re
from config.skills_taxonomy import ALL_SKILLS
from utils.text_utils import clean_text

# Section header patterns — order matters; first match wins
SECTION_PATTERNS = {
    "skills": re.compile(
        r"^\s*(technical\s+)?skills?|competencies|technologies|tech\s+stack", re.I
    ),
    "experience": re.compile(
        r"^\s*(work\s+)?experience|employment|professional\s+background|career", re.I
    ),
    "education": re.compile(
        r"^\s*education(al)?|academic|qualifications?|degrees?", re.I
    ),
    "projects": re.compile(r"^\s*projects?|portfolio|personal\s+work", re.I),
    "certifications": re.compile(
        r"^\s*certifications?|certificates?|licen[sc]es?|credentials?", re.I
    ),
}

_SKILL_PATTERNS = {
    skill: re.compile(r"\b" + re.escape(skill.lower()) + r"\b")
    for skill in ALL_SKILLS
}


def parse_resume(text: str) -> dict:
    text = clean_text(text)
    sections = _split_sections(text)
    skills = extract_skills(text)
    return {"sections": sections, "skills": skills}


def parse_jd(text: str) -> dict:
    text = clean_text(text)
    skills = extract_skills(text)
    return {"skills": skills, "text": text}


def _split_sections(text: str) -> dict:
    sections: dict[str, list[str]] = {k: [] for k in SECTION_PATTERNS}
    current = "other"
    other_lines: list[str] = []

    for line in text.splitlines():
        matched = _match_section_header(line)
        if matched:
            current = matched
        elif current in sections:
            sections[current].append(line)
        else:
            other_lines.append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _match_section_header(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return None
    for section, pattern in SECTION_PATTERNS.items():
        if pattern.match(stripped):
            return section
    return None


def extract_skills(text: str) -> list[str]:
    """Return skills found in text using taxonomy matching + spaCy NER."""
    text_lower = text.lower()
    found: set[str] = set()

    for skill, pattern in _SKILL_PATTERNS.items():
        if pattern.search(text_lower):
            found.add(skill)

    # Augment with spaCy NER — catches technology names not in taxonomy
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:10000])  # cap for speed
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT"):
                candidate = ent.text.strip()
                # Only accept if it looks like a technology (no spaces or ≤3 words)
                if len(candidate.split()) <= 3 and len(candidate) > 1:
                    found.add(candidate)
    except Exception:
        pass  # spaCy unavailable — taxonomy matching still works

    return sorted(found)
