"""
File: agent_orchestrator.py

Purpose:
Routes the workflow based on the user's intent.

Responsibilities:
- Reads the user's intent from AgentState.
- Decides which node should execute next.
- Returns the next node name to LangGraph.

Owner: Member 1- Ritisha(orchestrator)
"""

from graph.state import AgentState

#Creating Route function
def route(state: AgentState) -> str :
    intent= state["user_intent"].lower()
    if "job" in intent:
        return "jobs"
    elif "roadmap" in intent:
        return "roadmap"
    elif "cover" in intent:
        return "cover_letter"
    elif "full" in intent:
        return "jobs"
    else:
        raise ValueError("Unknown user intent")
    #else:
        return "jobs"
    
