"""
File: agent/agent_jobs.py
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

# Configuration for Retrieval
# Adjust this value to 3, 5, or 8 to find the best tradeoff for your matching
RETRIEVAL_K = 5

def _derive_skill_gaps(matched_jobs: list) -> list:
    """
    Aggregates "missing_skills" across all matched jobs into a single flat,
    deduplicated list of strings for Member 4's roadmap agent.

    Args:
        matched_jobs: List of job match dicts returned by
            task_match_jobs.match_jobs(), each expected to contain a
            "missing_skills" list.

    Returns:
        list: Flat list of unique missing skill strings, order preserved
              by first appearance. Returns an empty list if there are no
              matched jobs or no missing skills anywhere.
    """
    seen = set()
    skill_gaps = []

    for job in matched_jobs:
        if not isinstance(job, dict):
            continue

        missing = job.get("missing_skills", [])
        if not isinstance(missing, list):
            continue

        for skill in missing:
            if not isinstance(skill, str):
                continue
            normalized = skill.strip()
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                skill_gaps.append(normalized)

    return skill_gaps


def run(state: AgentState) -> AgentState:
    """
    Runs the jobs agent: fetches live job listings for the target role,
    embeds and stores them in ChromaDB, retrieves the top-k listings most
    semantically similar to the resume embedding, matches them against the
    candidate's extracted skills, and derives the flat skill_gaps list
    that Member 4's roadmap agent depends on.

    Args:
        state: Current shared AgentState. Expects "target_role", "skills",
            and "resume_embedding" to already be populated.

    Returns:
        AgentState: Updated state with "raw_job_listings", "retrieved_chunks",
            "job_listings", and "skill_gaps" populated.
    """
    print(f"Jobs Agent Running (using K={RETRIEVAL_K})")

    target_role = state["target_role"]

    # Step 1: Fetch job listings (cached if available, else live API call)
    jobs = tool_jsearch.get_cached_or_fetch(target_role)
    state["raw_job_listings"] = jobs

    # Step 2: Embed and store job listings in ChromaDB
    print(f"DEBUG: Storing {len(jobs)} jobs in vector DB...")
    tool_rag_pipeline.embed_and_store(jobs)

    # Step 3: Retrieve top-k semantically similar jobs using the resume embedding
    # The K value is controlled by the constant defined at the top of this agent
    print(f"DEBUG: Resume Embedding exists? {state.get('resume_embedding') is not None}")
    if state.get("resume_embedding"):
        print(f"DEBUG: Embedding length: {len(state['resume_embedding'])}")

    retrieved_chunks = tool_rag_pipeline.retrieve_top_k(
        state["resume_embedding"], 
        k=RETRIEVAL_K
    )
    
    state["retrieved_chunks"] = retrieved_chunks

    # Step 4: Match retrieved jobs against the candidate's extracted skills
    matched_jobs = task_match_jobs.match_jobs(state["skills"], retrieved_chunks)
    state["job_listings"] = matched_jobs

    # Step 5: Derive skill_gaps (flat list of strings) for Member 4's roadmap agent
    state["skill_gaps"] = _derive_skill_gaps(matched_jobs)

    return state

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