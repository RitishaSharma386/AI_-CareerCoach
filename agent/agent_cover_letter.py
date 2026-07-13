"""
File: agent/agent_cover_letter.py
Owner: Member 4 — Shraddha Tyagi
Function: LangGraph agent node that generates a cover letter. Reads resume_json and one job listing from shared AgentState,
          calls task_generate_cover_letter.generate_cover_letter(), and
          returns the cover letter as a partial state update.
Location: agent/ folder — orchestrated by graph/graph.py.
"""
from task.task_generate_cover_letter import generate_cover_letter


def run(state: dict) -> dict:
    """
    Generates a tailored cover letter for the first job listing in state,
    based on the user's parsed resume, and returns it as a state update.

    Args:
        state: shared AgentState dict. Must contain "resume_json" (dict) and
               "job_listings" (list[dict], each with "company", "job_title",
               and "job_description" keys).

    Returns:
        dict with a single key "cover_letter" containing the generated letter.
        If job_description is under 50 words, skips generation and returns
        an error instead. On failure, returns {"cover_letter": None, "error": "<message>"}.
    """
    resume_json = state.get("resume_json", {})
    job_listings = state.get("job_listings", [])

    if not resume_json or not job_listings:
        return {"cover_letter": None, "error": "Missing resume_json or job_listings in state"}

    job = job_listings[0]  # picks the first job in the list
    job_description = job.get("job_description", "")

    if len(job_description.split()) < 50:
        return {"cover_letter": None, "error": "Job description too short to generate a meaningful cover letter."}

    try:
        cover_letter = generate_cover_letter(
            resume_json=resume_json,
            company=job.get("company", ""),
            job_description=job_description,
            job_title=job.get("job_title", ""),
        )
        return {"cover_letter": cover_letter}
    except Exception as e:
        return {"cover_letter": None, "error": str(e)}


if __name__ == "__main__":
    mock_state = {
        "resume_json": {
            "name": "Riya",
            "skills": ["Agentic AI", "Gen AI", "Data Science"],
            "experience": "null",
            "education": "B.Tech Computer Science",
            "projects": ["Agentic AI Productivity Tracker"],
            "target_role": "AI Engineer",
        },
        "job_listings": [
            {
                "company": "Google",
                "job_title": "AI Engineer",
                "job_description": (
                    "Work on Gemini model infrastructure and scalable ML systems. "
                    "Requires strong Python, distributed systems experience, and "
                    "familiarity with large-scale data pipelines and model serving "
                    "infrastructure for production AI workloads across global users."
                ),
            }
        ],
    }
    result = run(mock_state)
    print(result)
    