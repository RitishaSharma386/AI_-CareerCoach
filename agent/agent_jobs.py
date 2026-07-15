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

from collections import Counter

from tool.tool_jsearch import search_jobs
from tool.tool_rag_pipeline import embed_and_store, retrieve_top_k
from task.task_match_jobs import match_jobs


def _derive_skill_gaps(job_listings: list, top_n: int = 5) -> list:
    """
    Aggregates missing_skills across all matched jobs and ranks them by how
    often they show up — the more job listings that require a skill the
    candidate doesn't have, the higher priority it is for the roadmap (M4
    consumes this list directly).

    Args:
        job_listings: output of task_match_jobs.match_jobs()
        top_n: max number of skill gaps to return

    Returns:
        list[str]: skill gaps ordered from most to least frequently missing.
    """
    counter = Counter()
    for job in job_listings:
        for skill in job.get("missing_skills", []):
            counter[skill] += 1
    # most_common preserves insertion order for ties, which is fine here
    return [skill for skill, _ in counter.most_common(top_n)]


def run(state: dict) -> dict:
    """
    Runs the RAG job-matching pipeline and updates the shared AgentState.

    Reads:
        state["target_role"]: role to search for, e.g. "Software Engineer Intern"
        state["skills"]: list of candidate skills (from Member 2)
        state["resume_embedding"]: precomputed resume embedding vector (from Member 2)

    Writes:
        state["raw_job_listings"]: raw JSearch response
        state["retrieved_chunks"]: top-k semantically retrieved job chunks
        state["job_listings"]: Gemini/LLM-scored, ranked job matches
        state["skill_gaps"]: aggregated missing technical skills, most-needed first

    Returns:
        The updated state dict. On failure, sets state["error"] instead of
        raising, so the LangGraph node wrapper in graph/graph.py can route to
        END cleanly (per Member 1's error-handling convention).
    """
    print("Jobs Agent Running")

    target_role = state.get("target_role")
    skills = state.get("skills", [])
    resume_embedding = state.get("resume_embedding")

    # --- Confirm state["skills"] is actually coming through from M2 ---
    # Cheap visibility check: if M2 hasn't run yet or wrote the wrong key,
    # this will read as [] and you'll see it immediately in the logs instead
    # of silently getting empty matched_skills three steps later.
    print(f"[agent_jobs] state['skills'] read from M2: {skills}")
    if not skills:
        print("[agent_jobs] WARNING: state['skills'] is empty — did the resume "
              "agent (M2) run before this node? match_jobs() will have nothing "
              "to compare jobs against.")

    if not target_role:
        state["error"] = "agent_jobs: state['target_role'] is missing."
        return state
    if not resume_embedding:
        state["error"] = "agent_jobs: state['resume_embedding'] is missing — run the resume agent first."
        return state

    # Step 1: fetch raw job listings (cached to data/rawFolder/)
    raw_job_listings = search_jobs(target_role)
    state["raw_job_listings"] = raw_job_listings

    if not raw_job_listings:
        state["error"] = f"agent_jobs: no job listings found for role '{target_role}'."
        return state

    # Steps 2-3: embed job descriptions and store them in ChromaDB
    embed_and_store(raw_job_listings)

    # Steps 4-5: use the resume embedding (from M2) as the query vector and
    # retrieve the top-5 semantically similar jobs
    retrieved_chunks = retrieve_top_k(resume_embedding, k=5)
    state["retrieved_chunks"] = retrieved_chunks
    print(f"[agent_jobs] state['retrieved_chunks'] written: {len(retrieved_chunks)} chunks")

    if not retrieved_chunks:
        state["error"] = "agent_jobs: retrieval returned no chunks from an empty collection."
        return state

    # Step 6: LLM reasons over the retrieved chunks against the user's skills
    job_listings = match_jobs(skills, retrieved_chunks)
    state["job_listings"] = job_listings
    print(f"[agent_jobs] state['job_listings'] written: {len(job_listings)} scored jobs")

    # Aggregate skill gaps across all matched jobs for the roadmap agent (M4)
    skill_gaps = _derive_skill_gaps(job_listings)

    # M4 consumes this as a flat list[str] (it gets dropped straight into an
    # f-string prompt in task_generate_roadmap.py) — enforce that shape here
    # rather than let a malformed list silently reach M4's prompt.
    assert isinstance(skill_gaps, list) and all(isinstance(s, str) for s in skill_gaps), (
        f"agent_jobs: skill_gaps must be a flat list[str] for M4, got: {skill_gaps!r}"
    )
    state["skill_gaps"] = skill_gaps
    print(f"[agent_jobs] state['skill_gaps'] written (flat list[str]): {skill_gaps}")

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