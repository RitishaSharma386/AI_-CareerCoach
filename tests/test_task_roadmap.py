"""
File: tests/test_task_roadmap.py
Owner: Member 4 — Shraddha Tyagi
Function: Unit tests for task_generate_roadmap.generate_roadmap() — the raw
          LLM-calling function, independent of the agent wrapper's guards.
"""

import re

from task.task_generate_roadmap import generate_roadmap


def normalize_text(text: str) -> str:
    """
    Normalize LLM output to avoid failures caused by Unicode spaces,
    fancy hyphens, and inconsistent formatting.
    """

    # Convert to lowercase
    text = text.lower()

    # Replace common Unicode spaces with a normal space
    unicode_spaces = [
        "\u00A0",  # No-break space
        "\u2007",  # Figure space
        "\u2009",  # Thin space
        "\u202F",  # Narrow no-break space
    ]

    for space in unicode_spaces:
        text = text.replace(space, " ")

    # Replace common Unicode hyphens/dashes with normal hyphen
    unicode_hyphens = [
        "\u2010",  # Hyphen
        "\u2011",  # Non-breaking hyphen
        "\u2012",  # Figure dash
        "\u2013",  # En dash
        "\u2014",  # Em dash
    ]

    for dash in unicode_hyphens:
        text = text.replace(dash, "-")

    # Collapse multiple whitespace characters
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def test_generate_roadmap_returns_string():
    result = generate_roadmap(
        "Software Engineer Intern",
        ["Docker", "SQL"]
    )

    assert isinstance(result, str)
    assert result.strip() != ""

    print("✅ test_generate_roadmap_returns_string passed")


def test_generate_roadmap_no_urls():
    result = generate_roadmap(
        "Data Scientist",
        ["Pandas", "Statistics"]
    )

    lower = result.lower()

    assert "http://" not in lower
    assert "https://" not in lower
    assert "www." not in lower

    print("✅ test_generate_roadmap_no_urls passed")


def test_generate_roadmap_mentions_all_weeks():
    result = generate_roadmap(
        "Frontend Developer",
        ["React", "CSS"]
    )

    print("\n========== RAW OUTPUT ==========")
    print(result)
    print("================================\n")

    normalized = normalize_text(result)

    # Print repr() for easier debugging if needed
    print("Normalized repr():")
    print(repr(normalized))

    for week in range(1, 5):
        pattern = rf"week[\s-]*{week}"

        assert re.search(
            pattern,
            normalized
        ), f"Could not find 'Week {week}' in roadmap."

    print("✅ test_generate_roadmap_mentions_all_weeks passed")


if __name__ == "__main__":
    test_generate_roadmap_returns_string()
    test_generate_roadmap_no_urls()
    test_generate_roadmap_mentions_all_weeks()

    print("\n🎉 All roadmap task tests passed.")