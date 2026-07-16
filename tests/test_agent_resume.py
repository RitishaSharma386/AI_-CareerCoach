"""
Test cases for resume agent utilities.
Member 2 - Kashish Dhingra
"""

from task.task_extract_skills import clean_json


def test_json_structure():
    result = clean_json(
        '{"name":"Kashish","skills":["Python"],"experience":[],"education":[],"projects":[],"target_role":"ML Engineer Intern"}'
    )

    keys = [
        "name",
        "skills",
        "experience",
        "education",
        "projects",
        "target_role"
    ]

    if all(key in result for key in keys):
        print("PASS: JSON structure test")
    else:
        print("FAIL: JSON structure test")


def test_empty_skills():
    result = clean_json(
        '{"name":"Test","skills":[],"experience":[],"education":[],"projects":[],"target_role":""}'
    )

    if "skills_message" in result:
        print("PASS: Empty skills fallback test")
    else:
        print("FAIL: Empty skills fallback test")


def test_skills_conversion():
    result = clean_json(
        '{"name":"Test","skills":"Python, C++","experience":[],"education":[],"projects":[],"target_role":""}'
    )

    if isinstance(result["skills"], list):
        print("PASS: Skills conversion test")
    else:
        print("FAIL: Skills conversion test")


def test_missing_fields():
    result = clean_json(
        '{"name":"Test","skills":["Python"]}'
    )

    if "experience" in result and "projects" in result:
        print("PASS: Missing fields handling test")
    else:
        print("FAIL: Missing fields handling test")


def test_target_role():
    result = clean_json(
        '{"name":"Test","skills":["Python","ML"],"experience":[],"education":[],"projects":[],"target_role":"ML Engineer Intern"}'
    )

    if result["target_role"]:
        print("PASS: Target role test")
    else:
        print("FAIL: Target role test")


if __name__ == "__main__":

    test_json_structure()
    test_empty_skills()
    test_skills_conversion()
    test_missing_fields()
    test_target_role()