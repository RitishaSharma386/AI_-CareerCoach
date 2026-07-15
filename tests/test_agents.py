"""
File: tests/test_agents.py
Owner: Member 4 — Shraddha Tyagi
Function: Mock-state tests for agent_roadmap.run() and agent_cover_letter.run(),
          covering normal input and both guard conditions.
"""
from agent import agent_roadmap, agent_cover_letter


def test_roadmap_normal():
    state = {
        "target_role": "Software Engineer Intern",
        "skill_gaps": ["Docker", "System Design", "SQL"],
    }
    result = agent_roadmap.run(state)
    assert result.get("roadmap")
    assert "error" not in result
    print("test_roadmap_normal passed")


def test_roadmap_empty_skill_gaps():
    state = {
        "target_role": "Software Engineer Intern",
        "skill_gaps": [],
    }
    result = agent_roadmap.run(state)
    assert result["roadmap"] == "Your profile already matches this role well!"
    print("test_roadmap_empty_skill_gaps passed")


def test_cover_letter_normal():
    state = {
        "resume_json": {
            "name": "Riya",
            "skills": ["Agentic AI", "Gen AI", "Data Science"],
            "projects": ["Agentic AI Productivity Tracker"],
        },
        "job_listings": [
            {
                "company": "Google",
                "job_title": "AI Engineer",
                "job_description": (
                    "Work on Gemini model infrastructure and scalable machine learning systems "
                    "that serve millions of users worldwide. This role requires strong Python "
                    "programming skills, hands-on experience with distributed systems, and deep "
                    "familiarity with large-scale data pipelines, model serving infrastructure, "
                    "and production AI workloads. You will collaborate closely with research "
                    "teams to optimize inference latency, improve model reliability, and design "
                    "systems that scale efficiently across global data centers and diverse "
                    "hardware environments."
                ),
            }
        ],
    }
    result = agent_cover_letter.run(state)
    assert result.get("cover_letter")
    assert "error" not in result
    print("test_cover_letter_normal passed")


def test_cover_letter_short_job_description():
    state = {
        "resume_json": {"name": "Riya", "skills": ["Gen AI"]},
        "job_listings": [
            {
                "company": "Google",
                "job_title": "AI Engineer",
                "job_description": "Short JD.",
            }
        ],
    }
    result = agent_cover_letter.run(state)
    assert result["cover_letter"] is None
    assert "error" in result
    print("test_cover_letter_short_job_description passed")


def test_cover_letter_missing_job_listings():
    state = {"resume_json": {"name": "Riya"}, "job_listings": []}
    result = agent_cover_letter.run(state)
    assert result["cover_letter"] is None
    assert "error" in result
    print("test_cover_letter_missing_job_listings passed")


if __name__ == "__main__":
    test_roadmap_normal()
    test_roadmap_empty_skill_gaps()
    test_cover_letter_normal()
    test_cover_letter_short_job_description()
    test_cover_letter_missing_job_listings()
    print("\nAll tests passed.")
