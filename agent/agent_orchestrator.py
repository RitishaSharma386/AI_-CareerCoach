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

    # -------------------------
    # Keyword Fallback
    # -------------------------

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

    # Stop if an error already exists
    if state["error"] is not None:
        return "end"

    # Classify the user's intent using the LLM
    intent = classify_intent(state["user_query"])

    # Save the predicted intent in state
    state["user_intent"] = intent

    # Map LLM intents to graph node names
    route_map = {
        "find_jobs": "jobs",
        "get_roadmap": "roadmap",
        "write_cover_letter": "cover_letter",
        "full_analysis": "jobs",
    }

    next_node = route_map.get(intent)

    if next_node is None:
        state["error"] = f"Invalid user intent: {intent}"
        return "end"

    return next_node


# ----------------------------------------
# Testing
# ----------------------------------------

# if __name__ == "__main__":

#     test_queries = [
#         "Find AI internships",
#         "Show me software engineer jobs",
#         "I want to become a Data Scientist",
#         "Give me a roadmap for AI",
#         "Write a cover letter for Google",
#         "Write a cover letter for Microsoft",
#         "Analyze my resume completely",
#         "Help me with jobs and roadmap",
#         "I need a career plan",
#         "Find internships and write a cover letter",
#     ]

#     for query in test_queries:

#         intent = classify_intent(query)

#         print(f"Query  : {query}")
#         print(f"Intent : {intent}")
#         print("-" * 50)