"""
Integration test for agent/agent_jobs.py — Day 5 checklist items:
1. Confirm state["retrieved_chunks"] and state["job_listings"] write back correctly.
2. Confirm state["skill_gaps"] is a flat list of strings for M4.

Run with: python -m test_agent_jobs_integration
(Requires OPENROUTER_API_KEY and JSEARCH_API_KEY set in .env)
"""

from agent.agent_jobs import run

mock_state = {
    "resume_text": "Experienced in Python, SQL, and Machine Learning.",
    "resume_json": {},
    "skills": ["Python", "SQL", "Machine Learning"],
    "resume_embedding": None,  # filled in below using the real embedding model
    "target_role": "Data Analyst",
    "raw_job_listings": [],
    "retrieved_chunks": [],
    "job_listings": [],
    "skill_gaps": [],
    "roadmap": "",
    "cover_letter": "",
    "user_intent": "jobs",
    "error": None,
}

# Generate a real resume_embedding using the same model M3's pipeline uses,
# so retrieve_top_k() gets a genuinely comparable vector (mirrors what M2's
# agent_resume.py is expected to produce).
from tool.tool_rag_pipeline import _get_encoder  # noqa: E402

encoder = _get_encoder()
mock_state["resume_embedding"] = encoder.encode(
    "Job requiring: " + ", ".join(mock_state["skills"])
).tolist()


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


print("Running agent_jobs.run() on mock state...\n")
result_state = run(mock_state)

print("\n===== Checks =====")

all_passed = True

# --- Check 1: retrieved_chunks and job_listings write back correctly ---
all_passed &= check(
    "retrieved_chunks is a list",
    isinstance(result_state.get("retrieved_chunks"), list),
)
all_passed &= check(
    "retrieved_chunks is non-empty (assuming jobs were fetched)",
    len(result_state.get("retrieved_chunks", [])) > 0,
)
all_passed &= check(
    "job_listings is a list",
    isinstance(result_state.get("job_listings"), list),
)
all_passed &= check(
    "job_listings is non-empty",
    len(result_state.get("job_listings", [])) > 0,
)
if result_state.get("job_listings"):
    first_job = result_state["job_listings"][0]
    all_passed &= check(
        "each job_listings entry has match_score, matched_skills, missing_skills",
        isinstance(first_job, dict)
        and "match_score" in first_job
        and "matched_skills" in first_job
        and "missing_skills" in first_job,
    )

# --- Check 2: skill_gaps is a flat list of strings ---
skill_gaps = result_state.get("skill_gaps")
all_passed &= check("skill_gaps is a list", isinstance(skill_gaps, list))
all_passed &= check(
    "skill_gaps is flat (no nested lists/dicts)",
    isinstance(skill_gaps, list)
    and all(not isinstance(item, (list, dict)) for item in skill_gaps),
)
all_passed &= check(
    "skill_gaps contains only strings",
    isinstance(skill_gaps, list) and all(isinstance(item, str) for item in skill_gaps),
)

print("\n===== Final state summary =====")
print(f"raw_job_listings: {len(result_state.get('raw_job_listings', []))} items")
print(f"retrieved_chunks: {len(result_state.get('retrieved_chunks', []))} items")
print(f"job_listings:     {len(result_state.get('job_listings', []))} items")
print(f"skill_gaps:       {result_state.get('skill_gaps')}")
print(f"error:            {result_state.get('error')}")

print("\n===== Overall =====")
print("ALL CHECKS PASSED" if all_passed else "SOME CHECKS FAILED — see above")