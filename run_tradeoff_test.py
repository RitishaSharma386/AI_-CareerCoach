from agent import agent_jobs
from graph.state import AgentState
import json

# 1. Prepare the same "state" for each test
with open("data/resumes/my_resume.json", "r") as f:
    resume = json.load(f)

# Mock state based on your resume data
base_state = {
    "target_role": resume["target_role"],
    "skills": resume["skills"],
    "resume_embedding": [0.1] * 384  # Use a dummy embedding for the test logic
}

# 2. Run the test for different K values
for k_val in [3, 5, 8]:
    print(f"\n--- Testing K = {k_val} ---")
    
    # Temporarily override the K value for the agent
    agent_jobs.RETRIEVAL_K = k_val
    
    # Run the agent logic
    state = agent_jobs.run(base_state)
    
    # 3. Print the results for comparison
    print(f"Jobs found: {len(state['job_listings'])}")
    for job in state['job_listings']:
        print(f" - {job.get('job_title', 'N/A')}")