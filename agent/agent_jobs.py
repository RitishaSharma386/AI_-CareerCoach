"""
File: agent/agent_jobs.py
=======
Owner: Member 3 Priyanshi Saini
Function: Orchestrates the full RAG pipeline for job matching. Called by
          graph/graph.py's jobs_node. Reads state["skills"], state["target_role"],
          and state["resume_embedding"] (all produced by Member 2's resume
          agent), runs the 6-step pipeline (fetch -> embed -> store -> query
          -> retrieve -> reason), and writes state["raw_job_listings"],
          state["retrieved_chunks"], state["job_listings"], and
          state["skill_gaps"] back onto the shared AgentState.
Location: agent/ folder — registered as a node in graph/graph.py.

"""

from graph.state import AgentState
from tool import tool_jsearch
from tool import tool_rag_pipeline
from task import task_match_jobs

RETRIEVAL_K = 5

def _derive_skill_gaps(matched_jobs: list) -> list:
    seen = set()
    skill_gaps = []
    for job in matched_jobs:
        if not isinstance(job, dict): continue
        missing = job.get("missing_skills", [])
        if not isinstance(missing, list): continue
        for skill in missing:
            if not isinstance(skill, str): continue
            normalized = skill.strip()
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                skill_gaps.append(normalized)
    return skill_gaps

def run(state: AgentState) -> AgentState:
    print(f"Jobs Agent Running (using K={RETRIEVAL_K})")
    target_role = state["target_role"]

    jobs = tool_jsearch.get_cached_or_fetch(target_role)
    
    # Broaden query if empty
    if not jobs:
        print("No jobs found, broadening search query...")
        jobs = tool_jsearch.search_jobs(f"{target_role} AI developer")
        
    state["raw_job_listings"] = jobs

    # Guard against empty DB/Pipeline
    try:
        tool_rag_pipeline.embed_and_store(jobs)
    except Exception as e:
        state["error"] = f"Pipeline failed: {e}"
        return state

    retrieved_chunks = tool_rag_pipeline.retrieve_top_k(state["resume_embedding"], k=RETRIEVAL_K)
    state["retrieved_chunks"] = retrieved_chunks

    matched_jobs = task_match_jobs.match_jobs(state["skills"], retrieved_chunks)
    state["job_listings"] = matched_jobs
    state["skill_gaps"] = _derive_skill_gaps(matched_jobs)

    return state
"""

if __name__ == "__main__":
    # Manual/independent test: run `python agent/agent_jobs.py` from the
    # project root. Requires JSEARCH_API_KEY and OPENROUTER_API_KEY in .env
    # (or a pre-existing cache file in data/rawFolder/ for the target role).
    dummy_state = {
        "resume_text": "",
        "resume_json": {},
        "skills": ["Python", "SQL", "Docker"],
        "resume_embedding": None,  # replaced below with a real embedding
        "target_role": "Software Engineer Intern",
        "raw_job_listings": [],
        "retrieved_chunks": [],
        "job_listings": [],
        "skill_gaps": [],
        "roadmap": "",
        "cover_letter": "",
        "user_intent": "jobs",
        "error": None,
    }

    # In the real pipeline this comes from Member 2's task_extract_skills.py.
    # Here we generate a stand-in embedding so this file is testable on its own.
    from sentence_transformers import SentenceTransformer
    from graph.state import EMBEDDING_MODEL

    embedder = SentenceTransformer(EMBEDDING_MODEL)
    dummy_state["resume_embedding"] = embedder.encode(
        f"Job requiring: {', '.join(dummy_state['skills'])}"
    ).tolist()

    result = run(dummy_state)

    print("\n========== Final State (agent_jobs) ==========")
    print("Error:", result.get("error"))
    print("Raw job listings fetched:", len(result.get("raw_job_listings", [])))
    print("Retrieved chunks:", len(result.get("retrieved_chunks", [])))
    print("Job listings (scored):", result.get("job_listings"))
    print("Skill gaps:", result.get("skill_gaps"))

    # Spot check: do matched_skills on the returned jobs actually overlap
    # with the skills we fed in? If this set is empty across every job while
    # skills was non-empty, something upstream (embedding, retrieval, or the
    # LLM prompt) is broken, not just "no matches happened to exist".
    input_skills = set(dummy_state["skills"])
    for job in result.get("job_listings", []) or []:
        overlap = input_skills.intersection(job.get("matched_skills", []))
        print(f"Spot check — '{job.get('job_title')}': matched_skills overlap with input skills = {overlap or 'NONE'}")

"""