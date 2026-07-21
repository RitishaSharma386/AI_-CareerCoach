"""
File: agent_orchestrator.py

Owner: Member 1 - Ritisha

Purpose:
Contains the routing logic for the AI Career Coach workflow.

Responsibilities:
- Uses OpenRouter to classify user intent.
- Falls back to keyword routing if LLM fails.
- Routes the workflow based on the predicted intent.
"""

from graph.state import AgentState
from tool.tool_llm_client import get_model


def classify_intent(user_input: str) -> str:
    """
    Uses OpenRouter to classify the user's intent.
    Falls back to keyword routing if the API fails
    or returns an unexpected value.
    """
    try:
        client = get_model()
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an intent classifier for an AI Career Coach.\n"
                        "Return ONLY one of these values exactly:\n"
                        "find_jobs\n"
                        "get_roadmap\n"
                        "write_cover_letter\n"
                        "full_analysis\n"
                        "Do not explain your answer."
                    ),
                },
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
            temperature=0,
        )

        intent = response.choices[0].message.content.strip().lower()

        valid_intents = {
            "find_jobs",
            "get_roadmap",
            "write_cover_letter",
            "full_analysis",
        }

        if intent in valid_intents:
            return intent

    except Exception as e:
        print("OpenRouter Error:", e)

    query = user_input.lower()

    if "job" in query or "jobs" in query or "internship" in query:
        return "find_jobs"
    elif "roadmap" in query or "career" in query:
        return "get_roadmap"
    elif "cover letter" in query:
        return "write_cover_letter"
    else:
        return "full_analysis"


def route(state: AgentState) -> str:
    """
    Determines the next node in the workflow.
    """
    
    if state.get("error"):
        return "end"

    # Check if the UI explicitly requested a specific agent
    intent = state.get("user_intent")

    #  If there is no explicit intent, use the LLM to classify the query
    if not intent or intent == "":
        intent = classify_intent(state.get("user_query", ""))
        state["user_intent"] = intent

    # Map both LLM intents and UI direct intents to graph node names
    route_map = {
        # LLM Intents
        "find_jobs": "jobs",
        "get_roadmap": "roadmap",
        "write_cover_letter": "cover_letter",
        "full_analysis": "end", 

        # Direct UI Intents (sent by app.py)
        "jobs": "jobs",
        "roadmap": "roadmap",
        "cover_letter": "cover_letter"
    }

    next_node = route_map.get(intent)

    if next_node is None:
        state["error"] = f"Invalid user intent: {intent}"
        return "end"

    return next_node

