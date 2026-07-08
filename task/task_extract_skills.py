"""
File: task/task_extract_skills.py
Owner: Member 2 — Kashish Dhingra
Function: Sends extracted resume text to LLM and extracts structured
          resume information in JSON format.
          Extracts name, skills, experience, education, projects,
          and target_role.
Location: task/ folder — called by agent/agent_resume.py.
"""

import json
from tool.tool_llm_client import get_model


def extract_resume_info(raw_text: str) -> dict:
    model = get_model()

    prompt = f"""
Extract structured information from this resume.

Use the exact information from the resume.
Do not modify names, company names, university names, or other proper nouns.

Verify extracted information carefully.
Preserve exact spellings of names, skills, technologies, universities, and acronyms.
If unsure, use the text exactly as provided and do not guess.

Return only JSON with these keys:
name,
skills,
experience,
education,
projects,
target_role.

Resume text:
{raw_text}
"""

    try:
        response = model.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        clean_response = (
            response.choices[0]
            .message.content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        resume_data = json.loads(clean_response)

        return resume_data

    except Exception as e:
        print(f"Error extracting resume information: {e}")
        return {}