"""
File: agent/agent_roadmap.py
Owner: Member 4 — Shraddha Tyagi
Function: LangGraph agent node that generates a 4-week learning roadmap.Reads target_role and skill_gaps from shared AgentState, calls
          task_generate_roadmap.generate_roadmap(), and returns the roadmap
          as a partial state update.
Location: agent/ folder — orchestrated by graph/graph.py.
"""
from task.task_generate_roadmap import generate_roadmap


def run(state: dict) -> dict:
    """
    Generates a personalized 4-week roadmap based on the user's target role
    and skill gaps, and returns it as a state update.
    Args:
        state: shared AgentState dict. Must contain "target_role" (str) and
               "skill_gaps" (list[str]).

    Returns:
        dict with a single key "roadmap" containing the generated plan.
        On failure, returns {"roadmap": None, "error": "<message>"} instead
        of crashing the whole graph.
    """
    target_role = state.get("target_role", "")
    skill_gaps = state.get("skill_gaps", [])

    if not target_role or not skill_gaps:
        return {"roadmap": None, "error": "Missing target_role or skill_gaps in state"}

    try:
        roadmap = generate_roadmap(target_role, skill_gaps)
        return {"roadmap": roadmap}
    except Exception as e:
        return {"roadmap": None, "error": str(e)}


if __name__ == "__main__":
    mock_state = {
        "target_role": "Software Engineer Intern",
        "skill_gaps": ["Docker", "System Design", "SQL"],
    }
    result = run(mock_state)
    print(result)
    
# def run(state):

#     print("Roadmap Agent Running")

#     state["roadmap"] = "Learn Docker"

#     return state