"""
File: agent_orchestrator.py

Owner: Member 1 - Ritisha

Purpose:
Contains the routing logic for the AI Career Coach workflow.

Responsibilities:
- Checks if an error occurred during graph execution.
- Routes the workflow based on the user's intent.
- Returns the name of the next node for LangGraph.
"""

from graph.state import AgentState


def route(state: AgentState) -> str:
    """
    Determines the next node in the workflow.

    Priority:
    1. If an error exists, stop the workflow.
    2. Otherwise, route according to the user's intent.

    Args:
        state: Current shared AgentState.

    Returns:
        str: Name of the next node ("jobs", "roadmap",
             "cover_letter", or "end").
    """

    # Stop the workflow if any error has occurred
    if state["error"] is not None:
        return "end"

    # Read the user's intent
    intent = state["user_intent"]

    # Route based on intent
    if intent == "jobs":
        return "jobs"

    elif intent == "roadmap":
        return "roadmap"

    elif intent == "cover_letter":
        return "cover_letter"

    # Invalid intent
    else:
        state["error"] = f"Invalid user intent: {intent}"
        return "end"