"""
File: agent/agent_jobs.py
Owner: Member 3 - Priyanshi Saini
Function: Orchestrates the full RAG pipeline: fetching jobs, embedding,
          storing, and triggering the matching task. Also derives
          state["skill_gaps"] (a flat, deduplicated list of missing
          technical skills across all matched jobs) for Member 4's
          roadmap agent, since this node runs immediately before it.
Location: agent/ folder — called by graph/graph.py.
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
    tool_rag_pipeline.embed_and_store(jobs)

    # Step 3: Retrieve top-k semantically similar jobs using the resume embedding
    # The K value is controlled by the constant defined at the top of this agent
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