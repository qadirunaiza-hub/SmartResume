# SmartResume – AI Resume Analyzer

A production-quality Python/Streamlit app that compares a resume against a job description using **transparent NLP scoring** and optional **GenAI suggestions** via the Anthropic API.

---

## Quick Start

```bash
cd smartresume
chmod +x setup.sh && ./setup.sh   # creates venv, installs deps, downloads spaCy model
source venv/bin/activate
streamlit run app.py
```

For AI suggestions, add your Anthropic key to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Project Structure

```
smartresume/
├── app.py                      # Streamlit UI entry point
├── requirements.txt
├── setup.sh
├── .env.example
├── config/
│   └── skills_taxonomy.py      # Curated skill list by category
├── core/
│   ├── extractor.py            # PDF / DOCX text extraction
│   ├── parser.py               # Section detection + skill extraction
│   ├── matcher.py              # Score calculation (TF-IDF + skill overlap)
│   └── suggestions.py          # Rule-based + LLM suggestions
├── utils/
│   └── text_utils.py           # Text cleaning helpers
└── data/
    ├── sample_resume.txt       # Arjun Sharma – Software Engineer
    └── sample_jd.txt           # Senior Data Engineer role
```

---

## Score Formula

```
Final Score = 70% × Skill Match Score + 30% × Semantic Similarity
```

| Component | Weight | Calculation |
|-----------|--------|-------------|
| Skill Match | 70% | `|resume_skills ∩ jd_skills| / |jd_skills| × 100` |
| Semantic Similarity | 30% | TF-IDF cosine similarity (0–100) |

**Why 70/30?** Skills are the primary binary filter in hiring; semantic similarity picks up domain vocabulary, phrasing alignment, and soft keywords that raw skill lists miss.

---

## NLP Techniques — Interview Discussion Guide

### 1. TF-IDF (Term Frequency–Inverse Document Frequency)
**What it is:** Numerical statistic that reflects how important a word is to a document relative to a corpus.

```
TF(t, d)  = count of term t in document d / total terms in d
IDF(t)    = log(N / df(t))   where df = number of docs containing t
TF-IDF    = TF × IDF
```

**Why it works here:** Common words like "the", "and", "role" get low IDF scores. Rare, meaningful terms like "Kubernetes", "PySpark" get high scores — exactly what we want for resume matching.

**In code:** `sklearn.TfidfVectorizer(stop_words='english', ngram_range=(1,2))`

---

### 2. Cosine Similarity
**What it is:** Measures the angle between two TF-IDF vectors. Ranges 0–1 (1 = identical).

```
cosine_similarity(A, B) = (A · B) / (|A| × |B|)
```

**Why it's better than Euclidean distance:** Cosine is length-invariant. A short resume and a long resume discussing the same technologies score the same. Euclidean distance would penalise length differences.

**In code:** `sklearn.metrics.pairwise.cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])`

---

### 3. Named Entity Recognition (NER)
**What it is:** Identifies named entities (persons, organisations, products, locations) in text.

**In code:** `spacy.load("en_core_web_sm")` → `doc.ents` → filter `ORG`, `PRODUCT` labels.

**Why it helps:** Catches technology names that aren't in our taxonomy (e.g., company-specific tools, new frameworks). Acts as a dynamic supplement to the static skills list.

---

### 4. Tokenisation & Lemmatisation
**Tokenisation:** Split text into words/tokens at whitespace/punctuation boundaries.

**Lemmatisation:** Normalise word forms to their root (lemma):
- "running" → "run"
- "databases" → "database"
- "designed" → "design"

**Why it matters:** Ensures "manages" and "managed" both match the skill "management". spaCy's lemmatiser uses linguistic rules + lookup tables for accuracy.

---

### 5. Stop Word Removal
**What:** Filter out high-frequency, low-information words ("the", "and", "is", "was").

**Why:** Stop words dominate TF-IDF vectors and dilute the signal from meaningful terms. sklearn's built-in English stop word list removes ~318 common words.

---

### 6. Regex Pattern Matching
**Two uses in this project:**

a) **Section detection:** `re.compile(r'^\s*(technical\s+)?skills?|competencies', re.I)` matches section headers regardless of exact capitalisation or prefix words.

b) **Skill extraction:** `re.compile(r'\b' + re.escape(skill.lower()) + r'\b')` uses word boundaries (`\b`) to avoid partial matches ("Java" matching "JavaScript").

---

### 7. Jaccard-style Set Overlap
**What:** For skills specifically, we use set intersection rather than TF-IDF.

```
Skill Match = |resume_skills ∩ jd_skills| / |jd_skills|
```

**Why not TF-IDF for skills?** Skill presence is binary and intentional — a skill either exists or it doesn't. TF-IDF would reward mentioning "Python" 10 times, which doesn't mean you're 10× more proficient.

---

## Deterministic NLP vs. LLM — Design Decision

| Layer | Method | Properties |
|-------|--------|------------|
| Skill extraction | Taxonomy matching + NER | Deterministic, explainable, no hallucinations |
| Scoring | TF-IDF cosine + set overlap | Reproducible, same input = same output |
| Improvement tips | Rule-based logic | Instant, free, predictable |
| AI suggestions | `claude-opus-5` | Contextual, rich — but optional, clearly labelled |

**Key guarantee:** The LLM never fabricates skills the candidate doesn't have. It only advises on *how* to address gaps that were identified deterministically.

---

## Sample Output (Arjun Sharma vs. Senior Data Engineer JD)

```
Match Score: 38/100

Skill Match:    27.3% (matched: Python, SQL, Docker, AWS, Git, S3, Redis)
Semantic Sim:   19.1% (resume is backend-heavy; JD is data-pipeline focused)

Missing Skills: Apache Spark, Kafka, Airflow, dbt, Kubernetes, Scala,
                EMR, Glue, Redshift, Athena, Great Expectations

Top Suggestion: Build a personal project using PySpark on local mode or
                AWS EMR; add an Airflow DAG for orchestration.
```

This realistic mismatch demonstrates why the tool is useful — it surfaces concrete gaps, not a vague "improve your resume" message.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI |
| `spacy` + `en_core_web_sm` | NER + tokenisation |
| `scikit-learn` | TF-IDF + cosine similarity |
| `pypdf` | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `nltk` | Supplementary NLP utilities |
| `anthropic` | Optional AI suggestions |
| `python-dotenv` | `.env` key management |
