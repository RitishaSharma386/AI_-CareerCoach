"""
File: tests/test_task_cover_letter.py
Owner: Member 4 — Shraddha Tyagi
Function: Unit tests for task_generate_cover_letter.generate_cover_letter() —
          the raw LLM-calling function, independent of the agent wrapper's guards.
"""
from task.task_generate_cover_letter import generate_cover_letter

resume = {
    "name": "Riya",
    "skills": ["Agentic AI", "Gen AI", "Data Science"],
    "projects": ["Agentic AI Productivity Tracker"],
    "education": "B.Tech Computer Science",
}

job_description = (
    "Work on Gemini model infrastructure and scalable machine learning systems "
    "that serve millions of users worldwide. This role requires strong Python "
    "programming skills, hands-on experience with distributed systems, and deep "
    "familiarity with large-scale data pipelines and production AI workloads."
)


def test_generate_cover_letter_returns_string():
    result = generate_cover_letter(resume, "Google", job_description, "AI Engineer")
    assert isinstance(result, str)
    assert len(result) > 0
    print("test_generate_cover_letter_returns_string passed")


def test_generate_cover_letter_under_300_words():
    result = generate_cover_letter(resume, "Google", job_description, "AI Engineer")
    word_count = len(result.split())
    assert word_count <= 300, f"Expected <=300 words, got {word_count}"
    print(f"test_generate_cover_letter_under_300_words passed ({word_count} words)")


def test_generate_cover_letter_no_banned_phrases():
    result = generate_cover_letter(resume, "Amazon", job_description, "SDE Intern")
    lower_result = result.lower()
    banned = ["i am passionate about", "team player", "hard worker"]
    found = [p for p in banned if p in lower_result]
    assert not found, f"Found banned phrases: {found}"
    print("test_generate_cover_letter_no_banned_phrases passed")


def test_generate_cover_letter_has_greeting_and_signoff():
    result = generate_cover_letter(resume, "Microsoft", job_description, "Data Scientist")
    assert "dear" in result.lower()[:50], "Expected a greeting near the start"
    assert "riya" in result.lower()[-50:], "Expected a sign-off with the candidate's name near the end"
    print("test_generate_cover_letter_has_greeting_and_signoff passed")


if __name__ == "__main__":
    test_generate_cover_letter_returns_string()
    test_generate_cover_letter_under_300_words()
    test_generate_cover_letter_no_banned_phrases()
    test_generate_cover_letter_has_greeting_and_signoff()
    print("\nAll cover letter task tests passed.")