"""
File: task/task_generate_roadmap.py
Owner: Member 4 — Shraddha Tyagi
Function: Generates a 4-week personalized learning roadmap using Gemini API.
          Reads skill_gaps and target_role from AgentState. Prompts are loaded
          from prompts/prompt_roadmap.txt for easy iteration.
Location: task/ folder — called by agent/agent_roadmap.py.
"""
from tool.tool_gemini_client import get_model
def generate_roadmap(target_role:str , skill_gaps: list ) -> str:
    model = get_model()
    prompt = f"""
    If i want to become {target_role} and my skill gaps are {skill_gaps}
    provide a 4 week planner to the user with the platform names and the learning resources like coursera, youtube , upskill, cs50 etc.
    no URLs, platform names only.
    Give a structured Output in points for all the key tasks per week for each week like WEEK-1 ,WEEK-2, etc.
    Consider Beginner Level.
    Prioritize skills that are most commonly required in job listings first.
    divide the Skill as 1-2 skills per week , asumming 2 hrs of learning daily.
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    skill_gaps = ["Docker", "System Design", "SQL"]
    target_role = "Software Engineer Intern"
    result = generate_roadmap(target_role, skill_gaps)
    print(result)
    