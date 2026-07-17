"""
File: task/task_match_jobs.py
Owner: Member 3 - Priyanshi Saini
Function: Sends top-k retrieved job descriptions to the LLM (via OpenRouter)
          for reasoning. Returns a scored list with match_score,
          matched_skills, and missing_skills for each retrieved job.
"""
import json
import re
import time
from tool.tool_llm_client import get_model

def _clean_json_response(raw_text: str) -> str:
    if not raw_text: return ""
    text = raw_text.strip()
    # Remove markdown code blocks
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

def _build_prompt(skills: list, retrieved_chunks: list) -> str:
    formatted_chunks = "\n\n".join([f"JOB {i+1}:\n{chunk}" for i, chunk in enumerate(retrieved_chunks)])
    return f"""
You are an expert Career Coach. Analyze the jobs below and compare them to the candidate's skills.

Candidate Skills: {skills}

Retrieved Jobs:
{formatted_chunks}

---
INSTRUCTIONS:
1. For each job, return a JSON object with: job_title, company, match_score (0-10), matched_skills (list), missing_skills (list).
2. ONLY include skills in 'matched_skills' if they are explicitly found in the Job Description.
3. 'missing_skills' must only contain requirements listed in the Job Description that the candidate does NOT have.
4. DO NOT repeat the candidate's skills if they aren't relevant to the job.
5. If a job description is vague, assign a lower match_score.
6. Return ONLY a valid JSON array. No preamble, no markdown formatting.

Example Output Format:
[
  {{"job_title": "Data Scientist", "company": "Tech Corp", "match_score": 8, "matched_skills": ["Python"], "missing_skills": ["PyTorch"]}}
]
"""

def match_jobs(skills: list, retrieved_chunks: list, retries=2) -> list:
    if not retrieved_chunks: return []
    
    # DEBUG: See what we are sending to the LLM
    print(f"DEBUG: Matching {len(retrieved_chunks)} jobs. First chunk preview: {retrieved_chunks[0][:200]}...")
    
    client = get_model()
    prompt = _build_prompt(skills, retrieved_chunks)
    
    for attempt in range(retries + 1):
        try:
            # Note: For better reasoning, use "google/gemini-2.0-flash-lite-preview-02-05" 
            # if your environment permits.
            response = client.chat.completions.create(
                model="openrouter/free",
                messages=[{"role": "user", "content": prompt}],
            )
            raw_content = response.choices[0].message.content
            cleaned = _clean_json_response(raw_content)
            
            if "User Safety" in cleaned or "unsafe" in cleaned.lower():
                print(f"Attempt {attempt}: Safety refusal. Retrying...")
                continue
                
            parsed = json.loads(cleaned)
            
            if isinstance(parsed, list):
                for job in parsed:
                    score = job.get("match_score", 0)
                    job["match_score"] = max(0, min(10, float(score)))
                return parsed
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(2) # Increased backoff
            
    return []

if __name__ == "__main__":
    mock_skills = ["Python", "SQL", "Machine Learning"]
    mock_chunks = [
        "Title: Data Analyst\nCompany: Amazon\nDescription: Analyze e-commerce data using SQL and Python.",
        "Title: ML Engineer\nCompany: Meta\nDescription: Train and deploy machine learning models at scale.",
    ]
    results = match_jobs(mock_skills, mock_chunks)
    print(json.dumps(results, indent=2, ensure_ascii=False))