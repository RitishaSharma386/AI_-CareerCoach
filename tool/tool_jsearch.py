"""
File: tool/tool_jsearch.py
Owner: Member 3 -  Priyanshi Saini
Function: Wrapper around the JSearch API (via Open Web Ninja API). Fetches raw job
          listings for a given target role and caches the raw response to
          data/rawFolder/cache_{role}.json so repeated pipeline runs / demos
          don't burn API quota. This is Step 1 of the RAG pipeline:
          tool_jsearch.py -> tool_rag_pipeline.py -> task_match_jobs.py.
Location: tool/ folder — called by agent/agent_jobs.py.
"""

import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

JSEARCH_HOST = "api.openwebninja.com"
JSEARCH_URL = f"https://{JSEARCH_HOST}/jsearch/search-v2"
RAW_FOLDER = "data/rawFolder"


def _cache_path(role: str) -> str:
    """
    Builds a filesystem-safe cache path for a given role, e.g.
    "Software Engineer Intern" -> data/rawFolder/cache_software_engineer_intern.json
    """
    safe_role = re.sub(r"[^a-z0-9]+", "_", role.strip().lower()).strip("_")
    return os.path.join(RAW_FOLDER, f"cache_{safe_role}.json")


def _load_cache(role: str):
    """Returns cached job listings for this role, or None if no cache exists."""
    path = _cache_path(role)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _save_cache(role: str, job_listings: list) -> None:
    """Persists raw job listings to data/rawFolder/ so future calls skip the API."""
    os.makedirs(RAW_FOLDER, exist_ok=True)
    path = _cache_path(role)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(job_listings, f, indent=2)

def search_jobs(target_role: str, location: str = "", num_pages: int = 1, use_cache: bool = True) -> list:
    if use_cache:
        cached = _load_cache(target_role)
        if cached is not None:
            print(f"[tool_jsearch] Using cached results for '{target_role}'")
            return cached

    api_key = os.getenv("JSEARCH_API_KEY")
    if not api_key:
        raise RuntimeError(
            "JSEARCH_API_KEY not set in .env — required to call the JSearch API. "
            "OpenWeb Ninja keys start with 'ak_'."
        )

    query = target_role if not location else f"{target_role} in {location}"
    headers = {
        "x-api-key": api_key,
    }
    params = {
        "query": query,
        "page": "1",
        "num_pages": str(num_pages),
    }

    try:
        response = requests.get(JSEARCH_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict):
            job_listings = data.get("jobs", data.get("data", []))
        else:
            job_listings = []
    except requests.RequestException as e:
        # Fall back to cache if the live call fails but we have prior data
        cached = _load_cache(target_role)
        if cached is not None:
            print(f"[tool_jsearch] API call failed ({e}); falling back to cache.")
            return cached
        raise RuntimeError(f"JSearch API request failed: {e}") from e

    _save_cache(target_role, job_listings)
    return job_listings


if __name__ == "__main__":
    test_role = "Data Analyst Intern"
    try:
        results = search_jobs(test_role, location="India")
        print(f"Fetched {len(results)} job listings for '{test_role}'")
        if results and isinstance(results, list):
            print("Sample listing keys:", list(results[0].keys())[:8])
            print("First job title:", results[0].get("job_title"))
            print("First employer:", results[0].get("employer_name"))
    except RuntimeError as e:
        print("Test failed:", e)

        