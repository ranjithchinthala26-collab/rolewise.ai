import re
from pathlib import Path
from pypdf import PdfReader

SKILL_TERMS = [
    "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI", "Flask", "Django",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "REST API", "Docker", "Kubernetes", "Git", "Linux",
    "Machine Learning", "Deep Learning", "NLP", "RAG", "LLM", "TensorFlow", "PyTorch", "Pandas",
    "NumPy", "Scikit-learn", "ChromaDB", "Vector Database", "AWS", "Azure", "HTML", "CSS"
]

def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        import io
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix in {".txt", ".md"}:
        text = content.decode("utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file type. Upload a PDF or TXT file.")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 40:
        raise ValueError("Could not extract enough text. Please use a text-based PDF or TXT resume.")
    return text[:50000]

def extract_skills(text: str) -> list[str]:
    found = []
    lower = text.lower()
    for skill in SKILL_TERMS:
        if skill.lower() in lower and skill not in found:
            found.append(skill)
    return found[:25]

def extract_candidate_name(text: str) -> str:
    for line in [x.strip() for x in text.splitlines() if x.strip()][:8]:
        if len(line) < 60 and not any(ch.isdigit() for ch in line) and len(line.split()) <= 5:
            if not any(word in line.lower() for word in ["resume", "curriculum", "profile", "email", "phone"]):
                return line
    return "Candidate"
