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
from sentence_transformers import SentenceTransformer
from graph.state import EMBEDDING_MODEL



# Handles different response formats returned by the LLM and prepares clean JSON output
def clean_json(raw_response: str) -> dict:

    # Remove markdown wrappers if LLM returns JSON inside code blocks
    clean_response = raw_response.replace("```json", "")
    clean_response = clean_response.replace("```", "")
    clean_response = clean_response.strip()

    try:
        # Convert string response into Python dictionary
        data = json.loads(clean_response)

    except Exception:
        # Return default structure when response cannot be parsed
        return {
            "name": "",
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "target_role": ""
        }


    # Add missing fields to maintain a consistent resume JSON structure
    required_keys = [
        "name",
        "skills",
        "experience",
        "education",
        "projects",
        "target_role"
    ]


    for key in required_keys:
        if key not in data:

            if key in ["skills", "experience", "education", "projects"]:
                data[key] = []

            else:
                data[key] = ""


    # Convert skills string into list format if LLM returns comma-separated skills
    if isinstance(data["skills"], str):
        data["skills"] = [
            skill.strip()
            for skill in data["skills"].split(",")
        ]
    # Add fallback message when no skills are extracted
    if not data["skills"]:
        data["skills_message"] = "No technical skills could be extracted from the resume."


    return data


# Creates embedding vector from resume skills for similarity matching
def generate_resume_embedding(skills: list) -> list:

    # No embedding is generated if skills are unavailable
    if not skills:
        return []

    # Convert skills into a query format similar to job requirements
    query = f"Job requiring: {', '.join(skills)}"

    # Use the shared embedding model used by resume and job retrieval pipeline
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Encode the query into numerical vector representation
    embedding = model.encode(query)

    return embedding.tolist()


def extract_resume_info(raw_text: str) -> dict:
    # Initialize LLM client for resume information extraction
    model = get_model()

    prompt = f"""
Extract structured information from this resume.

Use the exact information from the resume.
Do not modify names, company names, university names, or other proper nouns.

Verify extracted information carefully.
Preserve exact spellings of names, skills, technologies, universities, and acronyms.
If unsure, use the text exactly as provided and do not guess.
If the resume already mentions a target role, extract that role.

If the target role is not directly mentioned, try to identify the most suitable entry-level role based on the candidate's skills, projects, educational background, and technologies.

For example:
- A candidate with Python, C++, DSA, and software-related projects can be considered for a Software Engineer Intern role.
- A candidate with Machine Learning, Python, and AI projects can be considered for a Machine Learning Engineer Intern role.
- A candidate with HTML, CSS, and JavaScript skills can be considered for a Frontend Developer Intern role.

Try to provide the most relevant role instead of leaving the target_role field empty when enough information is available.

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
        # Send resume text to LLM and get structured response
        response = model.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Validate and clean LLM output before returning
        resume_data = clean_json(
            response.choices[0].message.content
        )

        return resume_data

    except Exception as e:
        print(f"Error extracting resume information: {e}")
        return {}