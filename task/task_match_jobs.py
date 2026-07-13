"""
File: task/task_match_jobs.py
Owner: Member 3 - Priyanshi Saini
Function: Takes the top-k retrieved job chunks from tool_rag_pipeline.py and
          the user's skills, and asks the LLM (via tool_llm_client, same
          OpenRouter setup used by Member 4's tasks) to reason over each job:
          how well does it match, which skills are covered, and which are
          missing. Returns structured JSON so the agent/UI layer can render
          it directly. This is Step 6 of the RAG pipeline.
Location: task/ folder — called by agent/agent_jobs.py.
"""

import json
from tool.tool_llm_client import get_model


def match_jobs(skills: list, retrieved_chunks: list) -> list:
    """
    Scores each retrieved job chunk against the user's skills using the LLM.

    Args:
        skills: list of user skills, e.g. ["Python", "SQL", "LangGraph"]
        retrieved_chunks: output of tool_rag_pipeline.retrieve_top_k(), i.e.
                           list of {"document": str, "metadata": dict, "distance": float}

    Returns:
        list[dict]: one entry per job, each with:
            - job_title (str)
            - company (str)
            - match_score (int, 0-10)
            - matched_skills (list[str])
            - missing_skills (list[str])  # technical skills only

        Returns [] if retrieved_chunks is empty (nothing to reason over).
    """
    if not retrieved_chunks:
        print("[task_match_jobs] No retrieved chunks to score — returning [].")
        return []

    client = get_model()

    # Build a compact job list for the prompt: title, company, and the
    # embedded text (which already contains the description).
    jobs_for_prompt = [
        {
            "job_title": chunk["metadata"].get("title", "Unknown role"),
            "company": chunk["metadata"].get("company", "Unknown company"),
            "description": chunk["document"],
        }
        for chunk in retrieved_chunks
    ]

    prompt = f"""
You are a technical recruiter assistant. Compare the candidate's skills
against each job listing below and score the match.

Candidate skills: {skills}

Job listings:
{json.dumps(jobs_for_prompt, indent=2)}

For EACH job, return a JSON object with exactly these keys:
- "job_title": string
- "company": string
- "match_score": integer from 0 to 10 (10 = perfect skill match)
- "matched_skills": list of candidate skills that match this job's requirements
- "missing_skills": list of technical skills the job requires that the candidate lacks
  (technical/tooling skills only — no soft skills like "communication" or "teamwork")

Return ONLY a JSON array of these objects, one per job, in the same order
as the listings above. No explanation, no markdown formatting, JSON only.
"""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[{"role": "user", "content": prompt}],
    )
    raw_output = response.choices[0].message.content.strip()

    # Gemini/OpenRouter models sometimes wrap JSON in ```json fences — strip
    # those defensively before parsing.
    clean = raw_output.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"task_match_jobs: LLM did not return valid JSON.\n"
            f"Raw output was: {raw_output}"
        ) from e

    return parsed


if __name__ == "__main__":
    # Manual test: run `python task/task_match_jobs.py` from the project root.
    # Requires OPENROUTER_API_KEY in .env (same as test_connection.py).
    mock_skills = ["Python", "SQL", "Docker"]
    mock_chunks = [
        {
            "document": "Machine Learning Engineer at Acme AI. Build and deploy "
                         "ML pipelines using Python, PyTorch, and Docker. "
                         "Experience with SQL required.",
            "metadata": {"title": "Machine Learning Engineer", "company": "Acme AI"},
            "distance": 0.12,
        },
        {
            "document": "Frontend Developer at Webify. Build React interfaces, "
                         "work with REST APIs, and collaborate with designers.",
            "metadata": {"title": "Frontend Developer", "company": "Webify"},
            "distance": 0.55,
        },
    ]

    result = match_jobs(mock_skills, mock_chunks)
    print(json.dumps(result, indent=2))