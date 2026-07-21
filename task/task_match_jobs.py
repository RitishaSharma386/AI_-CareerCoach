"""
File: task/task_match_jobs.py
Owner: Member 3 - Priyanshi Saini
Function: Sends top-k retrieved job descriptions to the LLM (via OpenRouter)
          for reasoning. Returns a scored list with match_score,
          matched_skills, and missing_skills for each retrieved job.
Location: task/ folder — called by agent/agent_jobs.py.
"""

import json
import re

from tool.tool_llm_client import get_model


def _clean_json_response(raw_text: str) -> str:
    """
    Strips markdown code fences and surrounding whitespace from an LLM response.
    """
    if not raw_text:
        return ""
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _build_prompt(skills: list, retrieved_chunks: list) -> str:
    """
    Builds the prompt sent to the LLM with structured job input.
    """
    
    formatted_chunks = "\n\n".join([f"JOB {i+1}:\n{chunk}" for i, chunk in enumerate(retrieved_chunks)])
    
    return f"""
User skills: {skills}.

Analyze the following job descriptions and return a JSON array of objects.

Retrieved jobs:
{formatted_chunks}

For each job, return JSON with these exact fields:
- job_title
- company
- match_score (0-10)
- matched_skills (list)
- missing_skills (list)

CRITICAL INSTRUCTIONS:
- Return ONLY a valid JSON array.
- Do not include markdown fences, code blocks, or explanations.
- Ensure all brackets and braces are properly closed.
- DO NOT use trailing commas or semicolons. Output strict, valid JSON.
"""


def match_jobs(skills: list, retrieved_chunks: list) -> list:
    """
    Sends retrieved job descriptions to the LLM and returns a scored, 
    structured list of matches.
    """
    if not retrieved_chunks:
        print("match_jobs: no retrieved_chunks provided, nothing to match.")
        return []

    client = get_model()
    prompt = _build_prompt(skills, retrieved_chunks)
    
    print(f"DEBUG: Prompt content sent to LLM: {prompt[:300]}...")

    for attempt in range(3):
        try:
            print(f"DEBUG: Requesting job matches from LLM (Attempt {attempt + 1})...")
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b:free", # Using your team's preferred model
                max_tokens=3000, 
                messages=[{"role": "user", "content": prompt}],
            )
            raw_content = response.choices[0].message.content or ""
            
            # If the model glitches with the safety flag, trigger a retry
            if "User Safety: safe" in raw_content:
                print(f"DEBUG: Model returned safety flag on attempt {attempt + 1}. Retrying...")
                continue

            cleaned = _clean_json_response(raw_content)
            parsed = json.loads(cleaned)

            
            if isinstance(parsed, dict):
                for value in parsed.values():
                    if isinstance(value, list):
                        parsed = value
                        break
                else:
                    parsed = [parsed]

            if not isinstance(parsed, list):
                print(f"match_jobs: unexpected JSON shape after parsing: {type(parsed)}")
                return []
            
            # Attach the original job descriptions so the Cover Letter agent doesn't fail
            for i, job in enumerate(parsed):
                if i < len(retrieved_chunks):
                    job["job_description"] = retrieved_chunks[i]
                    
            return parsed

        except (json.JSONDecodeError, TypeError) as e:
            print(f"match_jobs: JSON parsing failed on attempt {attempt + 1}: {e}")
            print(f"match_jobs: raw response was: {raw_content!r}")
            
        except Exception as e:
            print(f"match_jobs: OpenRouter API call failed on attempt {attempt + 1}: {e}")
            

    # If it fails 3 times, return an empty list
    print("match_jobs: Failed to get a valid JSON response after 3 attempts.")
    return []


if __name__ == "__main__":
    # Test block
    mock_skills = ["Python", "SQL", "Machine Learning"]
    mock_chunks = [
        "Title: Data Analyst\nCompany: Amazon\nDescription: Analyze e-commerce data using SQL and Python.",
        "Title: ML Engineer\nCompany: Meta\nDescription: Train and deploy machine learning models at scale.",
    ]
    results = match_jobs(mock_skills, mock_chunks)
    print(json.dumps(results, indent=2, ensure_ascii=False))