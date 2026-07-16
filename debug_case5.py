from tool.tool_llm_client import get_model
from task.task_generate_cover_letter import generate_cover_letter

resume = {
    "name": "Riya",
    "skills": ["Agentic AI", "Gen AI", "Data Science"],
    "projects": ["Agentic AI Productivity Tracker"],
    "education": "B.Tech Computer Science",
}

result = generate_cover_letter(
    resume_json=resume,
    company="FinTrust",
    job_description="Build secure, scalable APIs for a fast-growing fintech product. Requires Node.js or Python, database design experience, and comfort working in a fast-paced startup environment with rapid iteration.",
    job_title="Backend Developer",
)
print(repr(result))