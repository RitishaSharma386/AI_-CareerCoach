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
    # --- FIX: Prevent re-parsing the resume on Tabs 2, 3, and 4 ---
    if state.get("resume_json") and state.get("skills"):
        print("DEBUG: Bypassing Resume Node (already parsed)")
        return state
    # --------------------------------------------------------------
    try:
        updated_state = agent_resume.run(state)
        return updated_state
    except Exception as e:
        state["error"] = str(e)
        print("Resume Node Error:", e)
        return state


def jobs_node(state: AgentState):
    try:
        updated_state = agent_jobs.run(state)
        return updated_state
    except Exception as e:
        state["error"] = str(e)
        print("Jobs Node Error:", e)
        return state


def roadmap_node(state: AgentState):
    try:
        updated_state = agent_roadmap.run(state)
        return updated_state
    except Exception as e:
        state["error"] = str(e)
        print("Roadmap Node Error:", e)
        return state


def cover_letter_node(state: AgentState):
    try:
        updated_state = agent_cover_letter.run(state)
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

def after_jobs(state: AgentState):
    """
    Determines the next step after the Jobs node.
    Continue only for full analysis.
    """
    if state["user_intent"] == "full_analysis":
        return "roadmap"
    return "end"


def after_roadmap(state: AgentState):
    """
    Determines the next step after the Roadmap node.
    Continue only for full analysis.
    """
    if state["user_intent"] == "full_analysis":
        return "cover_letter"
    return "end"


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

builder.add_conditional_edges(
    "jobs",
    after_jobs,
    {
        "roadmap": "roadmap",
        "cover_letter": "cover_letter", # FIX: Added to prevent KeyError
        "end": END,
    }
)

builder.add_conditional_edges(
    "roadmap",
    after_roadmap,
    {
        "cover_letter": "cover_letter",
        "end": END,
    }
)

builder.add_edge("cover_letter", END)

#Entry point:
builder.set_entry_point("resume")

#Compile graph
graph=builder.compile()

