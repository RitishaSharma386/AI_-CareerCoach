"""
File: main.py
Description: Command Line Interface (CLI) fallback for the AI Career Coach.
Allows developers to test the LangGraph routing and agents directly from the terminal.
"""

import os
from graph.graph import app as graph_app

def print_separator(title: str):
    print(f"\n{'='*20} {title} {'='*20}")

def main():
    print_separator("AI Career Coach CLI")
    
    # Check for required API keys
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY is missing from environment variables.")
        return

    # Initialize a blank AgentState
    state = {
        "resume_text": "",
        "resume_json": {},
        "skills": [],
        "resume_embedding": None,
        "target_role": "",
        "raw_job_listings": [],
        "retrieved_chunks": [],
        "job_listings": [],
        "skill_gaps": [],
        "roadmap": "",
        "cover_letter": "",
        "user_query": "full_analysis",
        "user_intent": None,
        "error": None,
    }

    # Step 1: Ingest Resume
    print("Step 1: Resume Processing")
    print("Paste your resume text below (Press Enter twice when done):")
    lines = []
    while True:
        line = input()
        if not line.strip():
            break
        lines.append(line)
    
    state["resume_text"] = "\n".join(lines)
    
    print("\nRunning Resume Extraction Agent...")
    state = graph_app.invoke(state)
    
    if state.get("error"):
        print(f"\nPipeline stopped due to error: {state['error']}")
        return

    print("\nExtraction Complete! Found Skills:")
    print(state.get("skills", []))

    # Step 2: Target Role & Action Selection
    print_separator("Select Next Action")
    state["target_role"] = input("Enter your target job role (e.g., Data Scientist): ").strip()
    
    print("\nAvailable Commands:")
    print("1: Find Jobs (jobs)")
    print("2: Generate Roadmap (roadmap)")
    print("3: Write Cover Letter (cover_letter)")
    
    choice = input("\nEnter the command number (1, 2, or 3): ").strip()
    
    command_map = {
        "1": "jobs",
        "2": "roadmap",
        "3": "cover_letter"
    }
    
    selected_intent = command_map.get(choice)
    
    if not selected_intent:
        print("Invalid choice. Exiting CLI.")
        return
        
    state["user_intent"] = selected_intent
    
    # Step 3: Execute targeted agent
    print(f"\nInvoking Graph for {selected_intent}...")
    final_state = graph_app.invoke(state)
    
    # Output Results
    print_separator("Final Output")
    
    if selected_intent == "jobs":
        jobs = final_state.get("job_listings", [])
        print(f"Found {len(jobs)} matched jobs.")
        for j in jobs:
            print(f"- {j.get('job_title', 'Unknown Title')} (Score: {j.get('match_score', 0)})")
            
    elif selected_intent == "roadmap":
        print(final_state.get("roadmap", "No roadmap generated."))
        
    elif selected_intent == "cover_letter":
        print(final_state.get("cover_letter", "No cover letter generated."))

if __name__ == "__main__":
    main()