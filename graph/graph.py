"""
File: graph.py

Owner:
Member 1 – Ritisha Sharma

Purpose:
This module defines and compiles the LangGraph workflow for the AI Career Coach project.

Responsibilities:
- Creates the StateGraph using AgentState.
- Registers all workflow nodes.
- Connects nodes using edges and conditional routing.
- Invokes individual AI agents.
- Handles exceptions raised by agents.
- Compiles the graph into an executable workflow.

Workflow:

START
   │
Resume
   │
Conditional Routing
 ┌──────────┬──────────────┬───────────────┐
 │          │              │
Jobs    Roadmap     Cover Letter
 │
 ▼
Roadmap
 │
 ▼
Cover Letter
 │
 ▼
END
"""



from graph.state import AgentState
from agent.agent_orchestrator import route
import agent.agent_resume as agent_resume
import agent.agent_jobs as agent_jobs
import agent.agent_roadmap as agent_roadmap
import agent.agent_cover_letter as agent_cover_letter
from langgraph.graph import StateGraph, END

builder = StateGraph(AgentState)

#Nodes:
def resume_node(state: AgentState):

    try:
        updated_state = agent_resume.run(state)
        # print("\n===== After Resume Node =====")
        # print(updated_state)

        return updated_state

    except Exception as e:
        state["error"] = str(e)
        print("Resume Node Error:", e)
        return state


def jobs_node(state: AgentState):

    try:
        updated_state = agent_jobs.run(state)
        # print("\n===== After Job Node =====")
        # print(updated_state)

        return updated_state

    except Exception as e:
        state["error"] = str(e)
        print("Jobs Node Error:", e)
        return state


def roadmap_node(state: AgentState):

    try:
        updated_state = agent_roadmap.run(state)
        # print("\n===== After Roadmap Node =====")
        # print(updated_state)

        return updated_state

    except Exception as e:
        state["error"] = str(e)
        print("Roadmap Node Error:", e)
        return state


def cover_letter_node(state: AgentState):

    try:
        updated_state = agent_cover_letter.run(state)
        # print("\n===== After Cover Letter Node =====")
        # print(updated_state)

        return updated_state

    except Exception as e:
        state["error"] = str(e)
        print("Cover Letter Node Error:", e)
        return state

#Register Nodes:
builder.add_node("resume",resume_node)
builder.add_node("jobs",jobs_node)
builder.add_node("roadmap",roadmap_node)
builder.add_node("cover_letter",cover_letter_node)

#Connect nodes:
builder.add_conditional_edges(
    "resume",
    route,
    {
        "jobs" : "jobs",
        "roadmap": "roadmap",
        "cover_letter": "cover_letter",
        "end": END    
    }
)
builder.add_edge("jobs","roadmap")
builder.add_edge("roadmap","cover_letter")

#Entry point:
builder.set_entry_point("resume")

#Compile graph
graph=builder.compile()




if __name__ == "__main__":
    dummy_state = {
        "resume_text": "I know Python",
        "resume_json": {},
        "skills": [],
        "resume_embedding": [],
        "target_role": "",
        "raw_job_listings": [],
        "retrieved_chunks": [],
        "job_listings": [],
        "skill_gaps": [],
        "roadmap": "",
        "cover_letter": "",
        "user_query": "Give me a roadmap to become a data scientist",
        "user_intent": "",
        "error": None,
    }
    result = graph.invoke(dummy_state)
    print("\n========== Final State ==========")
    print(result)