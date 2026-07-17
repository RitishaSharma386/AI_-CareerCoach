"""
File: tests/consistency_check.py
Owner: Member 4 — Shraddha Tyagi
Function: Runs generate_roadmap() 3x on identical input to observe
          output consistency/variance at temperature=0.
"""
from task.task_generate_roadmap import generate_roadmap

target_role = "Software Engineer Intern"
skill_gaps = ["Docker", "System Design", "SQL"]

for i in range(1, 4):
    print(f"\n{'='*60}\nRUN {i}\n{'='*60}")
    result = generate_roadmap(target_role, skill_gaps)
    print(result)