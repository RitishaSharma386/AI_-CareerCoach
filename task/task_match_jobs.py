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

    formatted_chunks = "\n\n".join(
        [f"JOB {i+1}:\n{chunk}" for i, chunk in enumerate(retrieved_chunks)]
    )

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

Return ONLY a valid JSON array.
Do not include markdown fences or explanations.
"""


def match_jobs(skills: list, retrieved_chunks: list) -> list:
    """
    Sends retrieved job descriptions to the LLM and returns a scored,
    structured list of matches.
    """

    print("\n========== ENTERED match_jobs() ==========")

    if not retrieved_chunks:
        print("match_jobs: no retrieved_chunks provided, nothing to match.")
        return []

    client = get_model()
    print("OpenRouter client created successfully.")

    prompt = _build_prompt(skills, retrieved_chunks)

    print("\n===== Prompt Sent to LLM =====")
    print(prompt)

    raw_content = ""

    try:
        print("\n===== Sending request to OpenRouter =====")

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        print("\n===== LLM RESPONSE RECEIVED =====")
        print(response)

        if not response.choices:
            print("match_jobs: No choices returned by the LLM.")
            return []

        raw_content = response.choices[0].message.content or ""

        print("\n===== Raw Content =====")
        print(raw_content)

    except Exception as e:
        print(f"\n===== OpenRouter Exception =====")
        print(e)
        return []

    cleaned = _clean_json_response(raw_content)

    print("\n===== Cleaned JSON =====")
    print(cleaned)

    try:
        print("\n===== Parsing JSON =====")
        parsed = json.loads(cleaned)
        print("JSON parsed successfully.")

    except (json.JSONDecodeError, TypeError) as e:
        print(f"match_jobs: failed to parse LLM response as JSON: {e}")
        print(f"match_jobs: raw response was:\n{raw_content}")
        return []

    # Handle {"jobs": [...]} format if returned
    if isinstance(parsed, dict):
        for value in parsed.values():
            if isinstance(value, list):
                parsed = value
                break
        else:
            parsed = [parsed]

    if not isinstance(parsed, list):
        print(f"match_jobs: unexpected JSON shape: {type(parsed)}")
        return []

    print("\n===== Returning Parsed Jobs =====")
    print(f"Number of matched jobs: {len(parsed)}")

    return parsed