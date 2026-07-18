# """
# File: agent_orchestrator.py

# Owner: Member 1 - Ritisha

# Purpose:
# Contains the routing logic for the AI Career Coach workflow.

# Responsibilities:
# - Uses OpenRouter to classify user intent.
# - Falls back to keyword routing if LLM fails.
# - Routes the workflow based on the predicted intent.
# """

# from graph.state import AgentState
# from tool.tool_llm_client import get_model


# def classify_intent(user_input: str) -> str:
#     """
#     Uses OpenRouter to classify the user's intent.
#     Falls back to keyword routing if the API fails
#     or returns an unexpected value.
#     """

#     try:
#         client = get_model()

#         response = client.chat.completions.create(
#             model="openai/gpt-oss-20b:free",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are an intent classifier for an AI Career Coach.\n"
#                         "Return ONLY one of these values exactly:\n"
#                         "find_jobs\n"
#                         "get_roadmap\n"
#                         "write_cover_letter\n"
#                         "full_analysis\n"
#                         "Do not explain your answer."
#                     ),
#                 },
#                 {
#                     "role": "user",
#                     "content": user_input,
#                 },
#             ],
#             temperature=0,
#         )

#         intent = response.choices[0].message.content.strip().lower()

#         valid_intents = {
#             "find_jobs",
#             "get_roadmap",
#             "write_cover_letter",
#             "full_analysis",
#         }

#         if intent in valid_intents:
#             return intent

#     except Exception as e:
#         print("OpenRouter Error:", e)

#     # -------------------------
#     # Keyword Fallback
#     # -------------------------

#     query = user_input.lower()

#     if "job" in query or "jobs" in query or "internship" in query:
#         return "find_jobs"

#     elif "roadmap" in query or "career" in query:
#         return "get_roadmap"

#     elif "cover letter" in query:
#         return "write_cover_letter"

#     else:
#         return "full_analysis"


# def route(state: AgentState) -> str:

#     print("\n========== ROUTE FUNCTION ==========")
#     print("User Query:", state["user_query"])

#     if state["error"] is not None:
#         return "end"

#     intent = classify_intent(state["user_query"])

#     print("Predicted Intent:", intent)

#     state["user_intent"] = intent

#     route_map = {
#         "find_jobs": "jobs",
#         "get_roadmap": "roadmap",
#         "write_cover_letter": "cover_letter",
#         "full_analysis": "jobs",
#     }

#     next_node = route_map.get(intent)

#     print("Next Node:", next_node)

#     if next_node is None:
#         state["error"] = f"Invalid user intent: {intent}"
#         return "end"

#     return next_node

# """
# File: agent_orchestrator.py

# Owner: Member 1 - Ritisha

# Purpose:
# Contains the routing logic for the AI Career Coach workflow.

# Responsibilities:
# - Uses OpenRouter to classify user intent.
# - Falls back to keyword routing if LLM fails.
# - Routes the workflow based on the predicted intent.
# """

# from graph.state import AgentState
# from tool.tool_llm_client import get_model


# def classify_intent(user_input: str) -> str:
#     """
#     Uses OpenRouter to classify user's intent.
#     Falls back to keyword routing if API fails
#     or returns an unexpected value.
#     """

#     try:
#         client = get_model()

#         response = client.chat.completions.create(
#             model="openai/gpt-oss-20b:free",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are an intent classifier for an AI Career Coach.\n"
#                         "Classify the user request into exactly ONE category.\n\n"
#                         "Allowed values:\n"
#                         "find_jobs\n"
#                         "get_roadmap\n"
#                         "write_cover_letter\n"
#                         "full_analysis\n\n"
#                         "Return ONLY the category name.\n"
#                         "Do not explain."
#                     ),
#                 },
#                 {
#                     "role": "user",
#                     "content": user_input,
#                 },
#             ],
#             temperature=0,
#         )

#         intent = (
#             response.choices[0]
#             .message.content
#             .strip()
#             .lower()
#             .replace(".", "")
#             .replace("`", "")
#         )

#         valid_intents = {
#             "find_jobs",
#             "get_roadmap",
#             "write_cover_letter",
#             "full_analysis",
#         }

#         if intent in valid_intents:
#             return intent

#         print("Unexpected LLM intent:", intent)

#     except Exception as e:
#         print("OpenRouter Error:", e)


#     # -------------------------
#     # Keyword Fallback
#     # -------------------------

#     query = user_input.lower()

#     # Check specific requests first

#     if "cover letter" in query:
#         return "write_cover_letter"

#     elif "roadmap" in query:
#         return "get_roadmap"

#     elif "job" in query or "jobs" in query or "internship" in query:
#         return "find_jobs"

#     else:
#         return "full_analysis"



# def route(state: AgentState) -> str:

#     print("\n========== ROUTE FUNCTION ==========")
#     print("User Query:", state["user_query"])


#     if state["error"] is not None:
#         return "end"


#     intent = classify_intent(state["user_query"])


#     print("Predicted Intent:", intent)


#     # Save detected intent
#     state["user_intent"] = intent

#     print("Saved Intent:", state["user_intent"])


#     route_map = {
#         "find_jobs": "jobs",
#         "get_roadmap": "roadmap",
#         "write_cover_letter": "cover_letter",
#         "full_analysis": "full_analysis",
#     }


#     next_node = route_map.get(intent)


#     print("Next Node:", next_node)


#     if next_node is None:
#         state["error"] = f"Invalid user intent: {intent}"
#         return "end"


#     return next_node

"""
File: agent_orchestrator.py

Owner: Member 1 - Ritisha

Purpose:
Contains intent classification and routing logic for AI Career Coach.

Responsibilities:
- Uses OpenRouter to classify user intent.
- Falls back to keyword routing if LLM fails.
- Updates AgentState with detected intent.
"""


from graph.state import AgentState
from tool.tool_llm_client import get_model



def classify_intent(user_input: str) -> str:
    """
    Uses OpenRouter to classify user's intent.
    Returns one of:
    - find_jobs
    - get_roadmap
    - write_cover_letter
    - full_analysis
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
                        "Return ONLY one value exactly:\n\n"
                        "find_jobs\n"
                        "get_roadmap\n"
                        "write_cover_letter\n"
                        "full_analysis\n\n"
                        "Do not explain."
                    ),
                },
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
            temperature=0,
        )


        intent = (
            response
            .choices[0]
            .message
            .content
            .strip()
            .lower()
            .replace(".", "")
            .replace("`", "")
        )


        valid_intents = {
            "find_jobs",
            "get_roadmap",
            "write_cover_letter",
            "full_analysis",
        }


        if intent in valid_intents:
            return intent


        print("Invalid LLM intent:", intent)


    except Exception as e:
        print("OpenRouter Error:", e)



    # -------------------------
    # Keyword fallback
    # -------------------------

    query = user_input.lower()


    if "cover letter" in query:
        return "write_cover_letter"


    elif "roadmap" in query:
        return "get_roadmap"


    elif (
        "job" in query
        or "jobs" in query
        or "internship" in query
    ):
        return "find_jobs"


    else:
        return "full_analysis"




def intent_router(state: AgentState):
    """
    LangGraph node.
    Classifies intent and updates state.
    """


    print("\n========== INTENT ROUTER ==========")
    print("User Query:", state["user_query"])


    if state["error"] is not None:
        return {
            "user_intent": "end"
        }


    intent = classify_intent(
        state["user_query"]
    )


    print("Predicted Intent:", intent)


    return {
        "user_intent": intent
    }