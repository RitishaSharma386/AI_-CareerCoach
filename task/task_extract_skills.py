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



# Clean and validate the LLM response before using it further
def clean_json(raw_response: str) -> dict:

    # Remove markdown formatting if the model wraps JSON inside ```json
    clean_response = raw_response.replace("```json", "")
    clean_response = clean_response.replace("```", "")
    clean_response = clean_response.strip()

    try:
        data = json.loads(clean_response)

    except Exception:
        # Return default structure if LLM response is not valid JSON
        return {
            "name": "",
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "target_role": ""
        }


    # Ensure all required fields are present
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


    # Sometimes LLM returns skills as a string instead of a list
    if isinstance(data["skills"], str):
        data["skills"] = [
            skill.strip()
            for skill in data["skills"].split(",")
        ]


    return data


# Generate an embedding from the extracted skills for resume matching
def generate_resume_embedding(skills: list) -> list:

    # Return an empty embedding if no skills are available
    if not skills:
        return []

    # Create a query that represents the candidate's skillset
    query = f"Job requiring: {', '.join(skills)}"

    # Load the shared embedding model used across resume and job embeddings
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Convert the query into an embedding vector
    embedding = model.encode(query)

    return embedding.tolist()


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

        # Clean the LLM response and convert it into structured JSON
        resume_data = clean_json(
            response.choices[0].message.content
        )

        return resume_data

    except Exception as e:
        print(f"Error extracting resume information: {e}")
        return {}
    

