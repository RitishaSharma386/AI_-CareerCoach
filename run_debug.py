from agent.agent_jobs import run
from graph.state import AgentState

# Simulate the state as if the Resume Agent already ran
test_state = {
    "resume_text": "Python Developer with AWS experience",
    "skills": ["Python", "AWS", "SQL"],
    "target_role": "software developer",
    "resume_embedding": [0.1] * 384, # Fake embedding to bypass the empty check
    "raw_job_listings": [],
    "retrieved_chunks": [],
    "job_listings": [],
    "skill_gaps": [],
    "roadmap": "",
    "cover_letter": "",
    "user_intent": "jobs",
    "error": None
}

print("Starting manual test...")
result = run(test_state)
print("Finished. Job listings found:", len(result.get("job_listings", [])))