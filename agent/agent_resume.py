
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
from task.task_extract_skills import extract_resume_info


def process_resume(pdf_path: str) -> dict:
    resume_text = extract_text(pdf_path)
    resume_data = extract_resume_info(resume_text)
    return resume_data

if __name__ == "__main__":
    pdf_path = input("Enter PDF path: ")

    result = process_resume(pdf_path)

    print(result)


