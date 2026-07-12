"""
File: graph/state.py
Owner: Member 1 — Ritisha (orchestrator)
Function: Defines the shared AgentState TypedDict that flows through all
          LangGraph nodes. All agents read from and write to this state.
Location: graph/ folder — imported by all agent and task files.
"""

from typing import TypedDict, Optional

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # M2 and M3 both import this constant

class AgentState(TypedDict):
    
    resume_text: str
    resume_json: dict
    skills: list
    resume_embedding : list
    target_role: str
    raw_job_listings: list      # raw JSearch results → saved to data/rawFolder/
    retrieved_chunks: list      # top-k semantic retrieval output
    job_listings: list          # Gemini-ranked final list
    skill_gaps: list
    roadmap: str
    cover_letter: str
    user_query: str 
    user_intent: str
    error: Optional[str]
    
