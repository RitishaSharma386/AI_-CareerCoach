# tests/test_multi_profile.py
'''
This script mocks the data Member 2 would have produced 
(the skills and resume embedding) to allow you to test  
M3 logic independently as in Day-6 .
Run full RAG pipeline on 3 profiles: junior dev, data analyst,
 ML engineer
'''
import sys
import os
import json

# Add project root to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_jobs import run
from graph.state import AgentState

# Define your test profiles
test_profiles = [
    {
        "name": "Junior Dev",
        "role": "Junior Software Engineer",
        "skills": ["Python", "Git", "HTML", "CSS"],
        "embedding": [0.01] * 384 # Mock embedding (use real vector in prod)
    },
    {
        "name": "Data Analyst",
        "role": "Data Analyst",
        "skills": ["SQL", "Pandas", "Tableau", "Excel"],
        "embedding": [0.02] * 384
    },
    {
        "name": "ML Engineer",
        "role": "Machine Learning Engineer",
        "skills": ["PyTorch", "TensorFlow", "AWS", "Scikit-Learn"],
        "embedding": [0.03] * 384
    }
]

def run_tests():
    for profile in test_profiles:
        print(f"\n--- Testing Profile: {profile['name']} ---")
        
        # 1. Prepare Mock State
        state: AgentState = {
            "target_role": profile["role"],
            "skills": profile["skills"],
            "resume_embedding": profile["embedding"],
            # Initializing other required keys as empty
            "raw_job_listings": [],
            "retrieved_chunks": [],
            "job_listings": [],
            "skill_gaps": [],
            "resume_text": "",
            "resume_json": {},
            "roadmap": "",
            "cover_letter": "",
            "user_query": "",
            "user_intent": "",
            "error": None
        }
        
        # 2. Execute Pipeline
        final_state = run(state)
        
        # 3. Save Results
        output_file = f"results_{profile['name'].replace(' ', '_').lower()}.json"
        with open(output_file, "w") as f:
            json.dump(final_state["job_listings"], f, indent=4)
        
        print(f"Successfully processed. Results saved to {output_file}")

if __name__ == "__main__":
    run_tests()