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
    # Format chunks clearly so the LLM doesn't get confused
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

Return ONLY a valid JSON array. Do not include any preamble, markdown fences, or explanations.
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
    
    # Debugging the input sent to the LLM
    print(f"DEBUG: Prompt content sent to LLM: {prompt[:300]}...")

    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_content = response.choices[0].message.content
    except Exception as e:
        print(f"match_jobs: OpenRouter API call failed: {e}")
        return []

    cleaned = _clean_json_response(raw_content)

    try:
        parsed = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"match_jobs: failed to parse LLM response as JSON: {e}")
        print(f"match_jobs: raw response was: {raw_content!r}")
        return []

    # Handle cases where the model returns an object like {"jobs": [...]}
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

    return parsed


if __name__ == "__main__":
    # Test block
    mock_skills = ["Python", "SQL", "Machine Learning"]
    mock_chunks = [
        "Title: Data Analyst\nCompany: Amazon\nDescription: Analyze e-commerce data using SQL and Python.",
        "Title: ML Engineer\nCompany: Meta\nDescription: Train and deploy machine learning models at scale.",
    ]
    results = match_jobs(mock_skills, mock_chunks)
    print(json.dumps(results, indent=2, ensure_ascii=False))