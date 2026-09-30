import re
import unicodedata

_WHITESPACE = re.compile(r"\s+")

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "this", "that", "these", "those", "i", "you", "he", "she", "it",
    "we", "they", "what", "which", "who", "whom", "how", "when", "where",
    "why", "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "just", "because", "if", "while", "although", "though",
    "also", "about", "above", "after", "before", "between", "into",
    "through", "during", "including", "until", "against", "among", "across",
}


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = _WHITESPACE.sub(" ", text)
    return text.strip()


def remove_stop_words(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t.lower() not in STOP_WORDS]


def simple_tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.]*\b", text)
    return tokens
