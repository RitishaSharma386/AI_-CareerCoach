"""
File: tests/eval_roadmap.py
Owner: Member 4 — Shraddha Tyagi
Function: Manual evaluation script — runs generate_roadmap() on 5 varied
          skill-gap lists to check specificity and scan for hallucinated URLs.
"""
import re
from task.task_generate_roadmap import generate_roadmap

test_cases = [
    ("Software Engineer Intern", ["Docker", "System Design", "SQL"]),
    ("Data Scientist", ["Pandas", "Statistics", "Machine Learning"]),
    ("Frontend Developer", ["React", "CSS", "TypeScript"]),
    ("DevOps Engineer", ["Kubernetes", "CI/CD", "AWS"]),
    ("AI Engineer", ["LangChain", "Prompt Engineering", "Vector Databases"]),
]

url_pattern = re.compile(r"https?://\S+|www\.\S+")

for i, (role, gaps) in enumerate(test_cases, 1):
    print(f"\n{'='*60}\nCASE {i}: {role} | Gaps: {gaps}\n{'='*60}")
    result = generate_roadmap(role, gaps)
    print(result)

    urls_found = url_pattern.findall(result)
    if urls_found:
        print(f"\n URLS FOUND (violates 'platform names only'): {urls_found}")
    else:
        print("\n No URLs detected")