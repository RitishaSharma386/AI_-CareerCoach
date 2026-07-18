import sys
import json

sys.stdout.reconfigure(encoding="utf-8")
import time
from graph.graph import graph
from tool.tool_pdf_parser import extract_text

resume_files = "data/resumes/resume1.pdf"

resume_text = extract_text(resume_files)
state = {
    "resume_text": resume_text,
    "resume_json": {},
    "skills": [],
    "resume_embedding": [],
    "target_role": "AI Engineer",
    "raw_job_listings": [],
    "retrieved_chunks": [],
    "job_listings": [],
    "skill_gaps": [],
    "roadmap": "",
    "cover_letter": "",
    "user_query": "Find AI jobs",
    "user_intent": "",
    "error": None
}
start = time.time()

result = graph.invoke(state)

end = time.time()

print("Intent:", result["user_intent"])
print("Jobs:", len(result["job_listings"]))
print("Skill Gaps:", len(result["skill_gaps"]))

print(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\nExecution Time: {end-start:.2f} seconds")