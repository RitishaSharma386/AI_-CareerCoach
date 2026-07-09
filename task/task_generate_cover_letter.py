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
    client = get_model()

    prompt = f"""
Generate a cover letter for my resume: {resume_json}.

Job Title: {job_title}
Company: {company}
Job Description: {job_description}

Instructions:
- Do not exceed 300 words.
- Do not use phrases like "I am passionate about" or "I am a team player".
- Mention 2-3 specific matching skills from the resume.
- Do not open with any variation of "I am writing to apply" or "I am excited to apply/submit" 
— open with a specific, concrete skill or achievement instead.
"""

    response = client.chat.completions.create(
    model="openrouter/free",
    messages=[{"role": "user", "content": prompt}]
)

    return response.choices[0].message.content


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
        company="Google",
        job_title="AI engineer",
        job_description="Manage Google Gemini's Models",
    )

    print(result)