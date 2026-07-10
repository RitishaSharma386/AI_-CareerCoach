
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
    resume_text = extract_text(pdf_path)
    resume_data = extract_resume_info(resume_text)
    return resume_data

def run(state: dict) -> dict:

    # Extract structured information from resume text
    resume_data = extract_resume_info(state["resume_text"])

    # Get skills from extracted resume JSON
    skills = resume_data.get("skills", [])

    # Generate embedding vector for resume skills
    resume_embedding = generate_resume_embedding(skills)

    # Update shared state
    state["resume_json"] = resume_data
    state["skills"] = skills

    # Store resume embedding for RAG matching
    state["resume_embedding"] = resume_embedding

    return state

if __name__ == "__main__":
    pdf_path = input("Enter PDF path: ")

    result = process_resume(pdf_path)

    print(result)


