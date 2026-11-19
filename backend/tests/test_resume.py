from app.services.resume import extract_skills, extract_candidate_name

def test_extracts_known_skills():
    text = "Ranjith Chinthala\nPython, FastAPI, MySQL and React projects"
    assert "Python" in extract_skills(text)
    assert "FastAPI" in extract_skills(text)
    assert "MySQL" in extract_skills(text)

def test_candidate_name_from_first_lines():
    assert extract_candidate_name("Ranjith Chinthala\nPython Developer\nEmail: test@example.com") == "Ranjith Chinthala"
