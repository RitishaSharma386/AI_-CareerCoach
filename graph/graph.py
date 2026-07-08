"""
File: graph.py

Owner: Member 1-Ritisha(orchestrator)

Purpose:
Creates and configures the LangGraph workflow for the AI Career Coach.

Responsibilities:
- Creates the StateGraph using AgentState.
- Registers all graph nodes.
- Connects nodes with edges.
- Sets the entry point.
- Compiles the graph into a runnable workflow.


"""


from langgraph.graph import StateGraph
from graph.state import AgentState
from agent.agent_orchestrator import route

builder = StateGraph(AgentState)

#Nodes:
def resume_node(state: AgentState):
    print("Resume node executed")
    return state

def job_node(state: AgentState):
    print("Job node executed")
    return state

def roadmap_node(state: AgentState):
    print("Roadmap node executed")
    return state

def cover_letter_node(state: AgentState):
    print("Cover letter node executed")
    return state

#Register Nodes:
builder.add_node("resume",resume_node)
builder.add_node("jobs",job_node)
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
    }
)
builder.add_edge("jobs","roadmap")
builder.add_edge("roadmap","cover_letter")

#Entry point:
builder.set_entry_point("resume")

#Compile graph
graph=builder.compile()


if __name__ == "__main__":


#------------------------------------
#Dummy State
#------------------------------------

  dummy_state = {
    "resume_text": "This is a sample resume",
    "resume_json": {},
    "skills": [],
    "target_role": "ML Engineer",
    "raw_job_listings": [],
    "retrieved_chunks": [],
    "job_listings": [],
    "skill_gaps": [],
    "roadmap": "",
    "cover_letter": "",
    "user_intent": "Full analysis",
    "error": None
  }
result = graph.invoke(dummy_state)
print(result)


