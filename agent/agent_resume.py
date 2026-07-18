
"""
File: agent/agent_resume.py
Owner: Member 2 — Kashish Dhingra
Function: Orchestrates the resume processing workflow.
          Calls the PDF parser tool to extract raw resume text
          and passes it to the skill extraction task for structured
          resume JSON generation.
Location: agent/ folder — called by agent_orchestrator.py.
"""

from tool.tool_pdf_parser import extract_text
from task.task_extract_skills import (
    extract_resume_info,
    generate_resume_embedding
)

def process_resume(pdf_path: str) -> dict:

    # Extract text content from the uploaded resume PDF
    resume_text = extract_text(pdf_path)
    # Convert extracted resume text into structured information
    resume_data = extract_resume_info(resume_text)
    return resume_data

def run(state: dict) -> dict:
    print("Step 1: Calling extract_resume_info()")

    # Extract structured resume details from the text stored in shared state
    resume_data = extract_resume_info(state["resume_text"])

    # Fetch skills from resume JSON because embeddings are generated using skills
    print("Step 2: resume_data")
    skills = resume_data.get("skills", [])
    print("Step 3: skills")
    print(skills)

    # Create embedding vector from skills for future similarity matching with jobs
    resume_embedding = generate_resume_embedding(skills)
    print("Step 4: embedding generated")

    # Save extracted resume information back into the shared graph state
    state["resume_json"] = resume_data
    state["skills"] = skills

    # Store embedding vector so other agents can use it for RAG-based matching
    state["resume_embedding"] = resume_embedding
    print("Step 5: State updated successfully")

    return state

if __name__ == "__main__":
    pdf_path = input("Enter PDF path: ")

    result = process_resume(pdf_path)

    print(result)


