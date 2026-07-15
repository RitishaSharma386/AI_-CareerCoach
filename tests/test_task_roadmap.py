"""
File: tests/test_task_roadmap.py
Owner: Member 4 — Shraddha Tyagi
Function: Unit tests for task_generate_roadmap.generate_roadmap() — the raw
          LLM-calling function, independent of the agent wrapper's guards.
"""
from task.task_generate_roadmap import generate_roadmap


def test_generate_roadmap_returns_string():
    result = generate_roadmap("Software Engineer Intern", ["Docker", "SQL"])
    assert isinstance(result, str)
    assert len(result) > 0
    print("test_generate_roadmap_returns_string passed")


def test_generate_roadmap_no_urls():
    result = generate_roadmap("Data Scientist", ["Pandas", "Statistics"])
    assert "http://" not in result and "https://" not in result and "www." not in result
    print("test_generate_roadmap_no_urls passed")


def test_generate_roadmap_mentions_all_weeks():
    result = generate_roadmap("Frontend Developer", ["React", "CSS"])
    lower_result = result.lower()
    for week in ["week-1", "week 1", "week‑1"]:
        if week in lower_result:
            break
    else:
        raise AssertionError("Expected some form of 'Week 1' labeling in output")
    print("test_generate_roadmap_mentions_all_weeks passed")


if __name__ == "__main__":
    test_generate_roadmap_returns_string()
    test_generate_roadmap_no_urls()
    test_generate_roadmap_mentions_all_weeks()
    print("\nAll roadmap task tests passed.")