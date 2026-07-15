"""
File: tests/test_m2_m3_integration.py
Owner: Member 3 - Priyanshi Saini
Function: End-to-end integration test for the M2 -> M3 handoff:
              PDF resume -> agent_resume (M2) -> skills + resume_embedding
              -> agent_jobs (M3) -> RAG retrieval -> ranked job_listings
          This runs the two real agents back to back against a single shared
          AgentState, exactly as graph/graph.py will when it's wired up.

Status: agent_resume.py (M2) is still a commented-out stub in this repo as
        of writing — it has no `run()` function yet. This test tries the
        real M2 agent first; if that's unavailable, it falls back to a
        MOCK resume-agent output (clearly logged as such) so M3's half of
        the contract can still be verified today. Swap USE_MOCK_M2 to False
        once M2 lands a real run() that returns skills + resume_embedding.
Location: tests/ folder — run directly, not imported elsewhere.
"""

import importlib

from graph.state import AgentState, EMBEDDING_MODEL
from agent import agent_jobs


def _try_real_agent_resume(state: dict):
    """
    Attempts to run the real Member 2 resume agent. Returns the updated
    state, or None if agent_resume.py doesn't yet expose a working run().
    """
    try:
        agent_resume = importlib.import_module("agent.agent_resume")
        if not hasattr(agent_resume, "run"):
            return None
        return agent_resume.run(state)
    except Exception as e:
        print(f"[integration test] Real agent_resume.run() unavailable/failed: {e}")
        return None


def _mock_agent_resume(state: dict) -> dict:
    """
    Stand-in for M2 until agent_resume.py is implemented. Produces the same
    state fields M3 depends on — skills (list[str]) and resume_embedding
    (384-dim vector from the SAME model M3 uses) — from a hardcoded resume
    text, so the M2/M3 contract can be exercised end-to-end today.
    """
    print("[integration test] MOCK agent_resume in use — replace with the "
          "real M2 agent once agent_resume.py implements run().")

    from sentence_transformers import SentenceTransformer
    resume_text = (
        "Experienced in Python, SQL, and machine learning. Built data "
        "pipelines and worked with Docker for deployment."
    )
    skills = ["Python", "SQL", "Machine Learning", "Docker"]

    embedder = SentenceTransformer(EMBEDDING_MODEL)
    state["resume_text"] = resume_text
    state["skills"] = skills
    state["resume_embedding"] = embedder.encode(resume_text).tolist()
    return state


def run_pipeline(target_role: str = "Software Engineer Intern") -> dict:
    """Builds a fresh AgentState and runs M2 (real or mock) -> M3 in sequence."""
    state: AgentState = {
        "resume_text": "",
        "resume_json": {},
        "skills": [],
        "resume_embedding": [],
        "target_role": target_role,
        "raw_job_listings": [],
        "retrieved_chunks": [],
        "job_listings": [],
        "skill_gaps": [],
        "roadmap": "",
        "cover_letter": "",
        "user_intent": "jobs",
        "error": None,
    }

    # Step A: M2 — resume -> skills + resume_embedding
    updated = _try_real_agent_resume(dict(state))
    if updated is None or not updated.get("skills") or not updated.get("resume_embedding"):
        state = _mock_agent_resume(state)
    else:
        state = updated

    # Step B: M3 — skills + resume_embedding -> RAG retrieval -> ranked jobs
    state = agent_jobs.run(state)
    return state


if __name__ == "__main__":
    # Manual test: run `python tests/test_m2_m3_integration.py` from the
    # project root. Requires JSEARCH_API_KEY and OPENROUTER_API_KEY in .env.
    final_state = run_pipeline()

    print("\n========== M2 -> M3 Integration Result ==========")
    print("Error:", final_state.get("error"))
    print("Skills (from M2):", final_state.get("skills"))
    print("Resume embedding length:", len(final_state.get("resume_embedding") or []))
    print("Retrieved chunks (M3):", len(final_state.get("retrieved_chunks", [])))
    print("Ranked job listings (M3):")
    for job in final_state.get("job_listings", []) or []:
        print(f"  - {job.get('job_title')} @ {job.get('company')} "
              f"| score={job.get('match_score')} "
              f"| matched={job.get('matched_skills')} "
              f"| missing={job.get('missing_skills')}")
    print("Skill gaps (for M4):", final_state.get("skill_gaps"))

    # Contract checks — these should never fail silently in a real run
    assert isinstance(final_state.get("skill_gaps"), list), "skill_gaps must be a list"
    assert all(isinstance(s, str) for s in final_state.get("skill_gaps", [])), \
        "skill_gaps must be a flat list of strings"
    print("\n[PASS] skill_gaps is a flat list[str] as required by M4.")