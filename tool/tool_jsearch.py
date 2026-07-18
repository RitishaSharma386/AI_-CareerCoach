"""
File: tool/tool_jsearch.py
Owner: Member 3 - Priyanshi
Function: Wrapper around JSearch API (OpenWeb Ninja) to fetch live job listings.
          Includes file-based caching to preserve free tier quota.
"""

import os
import json
import re
import time
import requests
from dotenv import load_dotenv

load_dotenv()

JSEARCH_HOST = "api.openwebninja.com"
JSEARCH_URL = f"https://{JSEARCH_HOST}/jsearch/search"

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")

RAW_FOLDER = os.path.join("data", "rawFolder")


def _safe_filename(role: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", role.strip().lower())
    return slug.strip("_") or "unknown_role"


def _cache_path(role: str) -> str:
    return os.path.join(RAW_FOLDER, f"cache_{_safe_filename(role)}.json")


def _ensure_raw_folder():
    os.makedirs(RAW_FOLDER, exist_ok=True)


def search_jobs(role: str, location: str = "India") -> list:

    if not JSEARCH_API_KEY:
        print("JSEARCH_API_KEY not found.")
        return []

    query = role

    headers = {
        "x-api-key": JSEARCH_API_KEY
    }

    params = {
        "query": query,
        "page": "1",
        "num_pages": "2"
    }

    print("QUERY SENT:", query)
    print("PARAMS:", params)

    data = None

    for attempt in range(3):

        try:

            print(f"\nAttempt {attempt+1}")

            response = requests.get(
                JSEARCH_URL,
                headers=headers,
                params=params,
                timeout=60
            )

            print("Status:", response.status_code)

            response.raise_for_status()

            data = response.json()

            break

        except requests.exceptions.Timeout:
            print("Timeout. Retrying...")
            time.sleep(3)

        except Exception as e:
            print("Request failed:", e)
            return []

    if data is None:
        return []

    print("\nFULL RESPONSE KEYS:", data.keys())

    # Save raw response
    _ensure_raw_folder()

    raw_path = os.path.join(
        RAW_FOLDER,
        f"raw_{_safe_filename(role)}.json"
    )

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # --------------------------
    # Extract jobs safely
    # --------------------------

    raw_list = []

    if isinstance(data, dict):

        inner = data.get("data")

        if isinstance(inner, dict):
            raw_list = inner.get("jobs", [])

        elif isinstance(inner, list):
            raw_list = inner

        else:
            raw_list = data.get("jobs", [])

    elif isinstance(data, list):
        raw_list = data

    print("Raw list type:", type(raw_list))
    print("Jobs fetched:", len(raw_list))

    job_listings = []

    for job in raw_list:

        if not isinstance(job, dict):
            continue

        job_listings.append({
            "job_title": job.get("job_title", ""),
            "employer_name": job.get("employer_name", ""),
            "job_description": job.get("job_description", ""),
            "job_apply_link": job.get("job_apply_link", ""),
            "job_location": job.get("job_location", ""),
            "job_employment_type": job.get("job_employment_type", "")
        })

    print("Normalized jobs:", len(job_listings))

    if job_listings:
        print("First Job:")
        print(json.dumps(job_listings[0], indent=2))

    _write_cache(role, job_listings)

    return job_listings


def _write_cache(role: str, jobs: list):

    _ensure_raw_folder()

    with open(_cache_path(role), "w", encoding="utf-8") as f:
        json.dump({"jobs": jobs}, f, indent=2, ensure_ascii=False)


def _read_cache(role: str):

    cache_file = _cache_path(role)

    if not os.path.exists(cache_file):
        return None

    try:

        with open(cache_file, "r", encoding="utf-8") as f:

            data = json.load(f)

            if isinstance(data, dict):
                return data.get("jobs", [])

            elif isinstance(data, list):
                return data

            return []

    except Exception:
        return None


def get_cached_or_fetch(role: str, location: str = "India"):

    cached = _read_cache(role)

    if cached is not None:

        print(f"Using cached job listings for role: '{role}'")

        return cached

    print(f"No cache found for role: '{role}'. Fetching...")

    return search_jobs(role, location)