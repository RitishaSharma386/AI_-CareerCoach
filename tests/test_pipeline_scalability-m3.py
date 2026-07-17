from agent import agent_jobs
from graph.state import AgentState

# Define 10 diverse skill sets based on your profile
test_scenarios = [
    
    {"target_role": "DevOps Engineer", "skills": ["Jenkins", "Linux", "Python", "Monitoring"]},
    {"target_role": "Full Stack Developer", "skills": ["JavaScript", "Node.js", "React", "MongoDB"]},
    {"target_role": "Quant Researcher", "skills": ["Mathematics", "C++", "Finance", "Time Series Analysis"]}
]

def run_scalability_test():
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*20} Testing Scenario {i+1}: {scenario['target_role']} {'='*20}")
        
        # Prepare the state
        base_state = {
            "target_role": scenario["target_role"],
            "skills": scenario["skills"],
            "resume_embedding": [0.1] * 384, # Using dummy for throughput test
            "job_listings": [],
            "raw_job_listings": [],
            "retrieved_chunks": [],
            "skill_gaps": []
        }
        
        # Run agent
        try:
            result = agent_jobs.run(base_state)
            
            # Spot check outputs
            print(f"Jobs found: {len(result['job_listings'])}")
            print(f"Skill gaps identified: {result['skill_gaps'][:3]}...") # Print first 3
            
        except Exception as e:
            print(f"Failed scenario {scenario['target_role']}: {e}")

if __name__ == "__main__":
    run_scalability_test()