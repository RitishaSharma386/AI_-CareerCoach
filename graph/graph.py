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
import agent.agent_resume as agent_resume
import agent.agent_jobs as agent_jobs
import agent.agent_roadmap as agent_roadmap
import agent.agent_cover_letter as agent_cover_letter

builder = StateGraph(AgentState)

#Nodes:
def resume_node(state: AgentState):

    updated_state = agent_resume.run(state)

    print("\n========== After Resume Node ==========")
    print(updated_state)

    return updated_state

def jobs_node(state: AgentState):

    updated_state = agent_jobs.run(state)

    print("\n========== After Jobs Node ==========")
    print(updated_state)

    return updated_state

def roadmap_node(state: AgentState):

    updated_state = agent_roadmap.run(state)

    print("\n========== After Roadmap Node ==========")
    print(updated_state)

    return updated_state

def cover_letter_node(state: AgentState):

    updated_state = agent_cover_letter.run(state)

    print("\n========== After Cover Letter Node ==========")
    print(updated_state)

    return updated_state

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
    "resume_text": "I know Python",
    "user_intent": "jobs",
    "skills": [],
    "job_listings": [],
    "roadmap": "",
    "cover_letter": ""
}
result = graph.invoke(dummy_state)

print("\n========== Final State ==========")
print(result)
