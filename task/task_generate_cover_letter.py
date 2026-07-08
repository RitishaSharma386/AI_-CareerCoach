"""
File: task/task_generate_cover_letter.py
Owner: M4 - Shraddha Tyagi
Function: Generate the cover letter by taking in the resume through parser and skills.
It uses Gemini API and gives the response under 300 words.
Location: task/
"""

from tool.tool_llm_client import get_model


def generate_cover_letter(
    resume_json: dict,
    company: str,
    job_description: str,
    job_title: str
) -> str:
    model = get_model()

    prompt = f"""
Generate a cover letter for my resume: {resume_json}.

Job Title: {job_title}
Company: {company}
Job Description: {job_description}

Instructions:
- Do not exceed 300 words.
- Do not start with "I am writing to apply".
- Do not use phrases like "I am passionate about" or "I am a team player".
- Mention 2-3 specific matching skills from the resume.
"""

    response = model.generate_content(prompt)

    return response.text


if __name__ == "__main__":
    mock_resume = {
        "name": "Riya",
        "skills": ["Agentic AI", "Gen AI", "Data Science"],
        "experience": "null",
        "education": "B.Tech Computer Science",
        "projects": ["Agentic AI Productivity Tracker"],
        "target_role": "AI Engineer",
    }

    result = generate_cover_letter(
        resume_json=mock_resume,
        company="...",
        job_title="...",
        job_description="...",
    )

    print(result)