"""
File: tool/tool_jsearch.py
Owner: Member 3 - Priyanshi
Function: Wrapper around JSearch API (OpenWeb Ninja) to fetch live job listings.
          Includes file-based caching to preserve free tier quota.
"""

import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

JSEARCH_HOST = "api.openwebninja.com"
JSEARCH_URL = f"https://{JSEARCH_HOST}/jsearch/search-v2"
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
        print("JSearch API Error: JSEARCH_API_KEY not set.")
        return []

    query = f"{role} in {location}"
    headers = {"x-api-key": JSEARCH_API_KEY}
    params = {"query": query, "page": "1", "num_pages": "1", "country": "in"}

    try:
        response = requests.get(JSEARCH_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # EXTRACT: Get the raw container
        raw_list = data.get("data") or data.get("jobs") or []
        
        # NORMALIZE: Ensure every item is a dictionary
        job_listings = []
        for item in raw_list:
            if isinstance(item, dict):
                job_listings.append(item)
            elif isinstance(item, str):
                # Attempt to parse string-formatted JSON
                try:
                    job_listings.append(json.loads(item))
                except json.JSONDecodeError:
                    continue
        
    except Exception as e:
        print(f"JSearch API request failed: {e}")
        return []

    _ensure_raw_folder()
    raw_path = os.path.join(RAW_FOLDER, f"raw_{_safe_filename(role)}.json")
    try:
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Warning: could not save raw response: {e}")

    _write_cache(role, job_listings)
    return job_listings

def _write_cache(role: str, job_listings: list):
    _ensure_raw_folder()
    cache_file = _cache_path(role)
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            # Standardize cache as a dictionary wrapper
            json.dump({"jobs": job_listings}, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Warning: could not write cache file: {e}")

def _read_cache(role: str) -> list:
    cache_file = _cache_path(role)
    if not os.path.exists(cache_file):
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Unwrap if it is the {"jobs": [...]} structure
            if isinstance(data, dict) and "jobs" in data:
                return data["jobs"]
            # Fallback if the cache is just a raw list
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError) as e:
        print(f"Warning: could not read cache file: {e}")
        return None

def get_cached_or_fetch(role: str, location: str = "India") -> list:
    _ensure_raw_folder()
    cached = _read_cache(role)
    if cached is not None:
        print(f"Using cached job listings for role: '{role}'")
        return cached
    print(f"No cache found for role: '{role}'. Fetching...")
    return search_jobs(role, location)