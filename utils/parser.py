import re
from functools import lru_cache
from typing import Any

import spacy
from spacy.language import Language

SKILLS: list[str] = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "FastAPI",
    "Django",
    "Flask",
    "SQL",
    "PostgreSQL",
    "MongoDB",
    "Redis",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Git",
    "Linux",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "REST API",
    "GraphQL",
    "CI/CD",
    "Agile",
    "Scrum",
    "C++",
    "C#",
    "Go",
    "Rust",
    "Kotlin",
    "Swift",
    "R",
    "Tableau",
    "Power BI",
    "Excel",
    "Spark",
    "Hadoop",
    "Kafka",
]

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(
    r"(?:(?<=\s)|(?<=^)|(?<=[(:]))(\+?\d[\d().\-\s]{5,}\d)"
)
NAME_FALLBACK_PATTERN = re.compile(
    r"^(?:[A-Z]\.?|[A-Z][a-zA-Z'-]+)(?:\s+(?:[A-Z]\.?|[A-Z][a-zA-Z'-]+)){1,3}$"
)
NAME_ALLOWED_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s.'-]*$")
DISALLOWED_NAME_TERMS = {
    "profile",
    "education",
    "experience",
    "projects",
    "skills",
    "technical",
    "languages",
    "frontend",
    "backend",
    "developer",
    "engineer",
    "intern",
    "resume",
    "curriculum",
    "vitae",
}


@lru_cache(maxsize=1)
def _load_nlp() -> Language | None:
    """Load the spaCy model once and reuse it across requests."""
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        return None


def _extract_name_with_spacy(raw_text: str) -> str | None:
    """Return the first PERSON entity detected by spaCy, if any."""
    nlp = _load_nlp()
    if nlp is None or not raw_text.strip():
        return None

    # spaCy NER is helpful but not perfect; headers and company names can still be misclassified.
    document = nlp(raw_text[:10000])
    for entity in document.ents:
        if entity.label_ == "PERSON":
            candidate = entity.text.strip()
            if _is_valid_name_candidate(candidate):
                return candidate

    return None


def _is_valid_name_candidate(candidate: str) -> bool:
    """Filter out obvious non-name entities such as skills or section labels."""
    cleaned_candidate = " ".join(candidate.split()).strip(" |,-")
    if not cleaned_candidate:
        return False

    if not NAME_ALLOWED_PATTERN.fullmatch(cleaned_candidate):
        return False

    normalized = cleaned_candidate.lower().replace(".", "")
    if normalized in {skill.lower() for skill in SKILLS}:
        return False

    words = [word for word in normalized.split() if word]
    if len(words) < 2 or len(words) > 4:
        return False

    if any(word in DISALLOWED_NAME_TERMS for word in words):
        return False

    if all(len(word) == 1 for word in words):
        return False

    return True


def _extract_name_from_header(raw_text: str) -> str | None:
    """Fallback name extractor based on the first five non-empty lines."""
    lines = [line.strip(" |,-") for line in raw_text.splitlines() if line.strip()]
    for line in lines[:5]:
        if NAME_FALLBACK_PATTERN.fullmatch(line) and _is_valid_name_candidate(line):
            return line
    return None


def extract_name(raw_text: str) -> str | None:
    """Extract a candidate name using spaCy first, then a simple header heuristic."""
    if not raw_text or not raw_text.strip():
        return None

    return _extract_name_from_header(raw_text) or _extract_name_with_spacy(raw_text)


def extract_emails(raw_text: str) -> list[str]:
    """Extract unique lowercase email addresses."""
    if not raw_text or not raw_text.strip():
        return []

    seen: set[str] = set()
    emails: list[str] = []
    for match in EMAIL_PATTERN.findall(raw_text):
        normalized = match.lower()
        if normalized not in seen:
            seen.add(normalized)
            emails.append(normalized)
    return emails


def _normalize_phone(phone: str) -> str | None:
    """Normalize a phone number to a stable representation."""
    cleaned = re.sub(r"[^\d+]", "", phone)
    digits = re.sub(r"\D", "", cleaned)
    if len(digits) < 7:
        return None

    has_plus_prefix = cleaned.startswith("+")

    if has_plus_prefix and len(digits) > 10:
        country_code = digits[:-10]
        local_number = digits[-10:]
        return f"+{country_code}-{local_number}"

    if len(digits) == 11 and digits.startswith("1"):
        return f"+1-{digits[1:]}"

    if len(digits) == 10:
        return f"+1-{digits}"

    return digits


def extract_phones(raw_text: str) -> list[str]:
    """Extract and normalize unique phone numbers."""
    if not raw_text or not raw_text.strip():
        return []

    seen: set[str] = set()
    phone_numbers: list[str] = []
    for match in PHONE_PATTERN.finditer(raw_text):
        normalized = _normalize_phone(match.group(1))
        if normalized and normalized not in seen:
            seen.add(normalized)
            phone_numbers.append(normalized)
    return phone_numbers


def extract_skills(raw_text: str) -> list[str]:
    """Match predefined skills in a case-insensitive way."""
    if not raw_text or not raw_text.strip():
        return []

    matched_skills: list[str] = []
    lowered_text = raw_text.lower()
    for skill in SKILLS:
        pattern = re.compile(rf"(?<!\w){re.escape(skill.lower())}(?!\w)")
        if pattern.search(lowered_text):
            matched_skills.append(skill)
    return matched_skills


def parse_resume(raw_text: str) -> dict[str, Any]:
    """Convert raw resume text into structured resume fields."""
    safe_text = raw_text if raw_text else ""
    return {
        "name": extract_name(safe_text),
        "email": extract_emails(safe_text),
        "phone": extract_phones(safe_text),
        "skills": extract_skills(safe_text),
    }


"""
Unit-testable examples:

1. parse_resume("John Doe\njohn@example.com\n+1 800 555 1234\nPython React Docker")
   -> {"name": "John Doe", "email": ["john@example.com"], "phone": ["+1-8005551234"], "skills": ["Python", "React", "Docker"]}

2. parse_resume("MARY JANE\nEmail: user.name+tag@sub.domain.org\nPhone: (123) 456-7890\nSkills: FastAPI, SQL, Git")
   -> name may be None from the fallback heuristic, email should include "user.name+tag@sub.domain.org",
      phone should include "+1-1234567890", skills should include ["FastAPI", "SQL", "Git"]

3. parse_resume("")
   -> {"name": None, "email": [], "phone": [], "skills": []}
"""
