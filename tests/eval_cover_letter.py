"""
File: tests/eval_cover_letter.py
Owner: Member 4 — Shraddha Tyagi
Function: Manual evaluation script — runs generate_cover_letter() on 5 varied
          job listings to check for generic/banned phrases.
"""
from task.task_generate_cover_letter import generate_cover_letter

resume = {
    "name": "Riya",
    "skills": ["Agentic AI", "Gen AI", "Data Science"],
    "projects": ["Agentic AI Productivity Tracker"],
    "education": "B.Tech Computer Science",
}

job_listings = [
    ("Google", "AI Engineer", "Work on Gemini model infrastructure and scalable ML systems serving millions of users. Requires strong Python, distributed systems experience, and familiarity with large-scale data pipelines and production AI workloads across global data centers."),
    ("Amazon", "SDE Intern", "Build backend services for the retail platform using Java and AWS. Requires knowledge of data structures, algorithms, distributed systems, and experience with cloud infrastructure and microservices architecture at scale."),
    ("Microsoft", "Data Scientist", "Analyze large datasets to drive product decisions across Azure services. Requires strong SQL, Python, statistics background, and experience building and deploying machine learning models in production environments."),
    ("Meta", "ML Engineer", "Design and deploy recommendation systems for billions of users. Requires deep learning experience, familiarity with PyTorch or TensorFlow, and strong understanding of distributed training and model optimization techniques."),
    ("FinTrust", "Backend Developer", "Build secure, scalable APIs for a fast-growing fintech product. Requires Node.js or Python, database design experience, and comfort working in a fast-paced startup environment with rapid iteration."),
]

banned_phrases = ["i am passionate about", "team player", "hard worker"]

for i, (company, title, desc) in enumerate(job_listings, 1):
    print(f"\n{'='*60}\nCASE {i}: {title} at {company}\n{'='*60}")
    result = generate_cover_letter(resume, company, desc, title)
    print(result)

    lower_result = result.lower()
    found = [p for p in banned_phrases if p in lower_result]
    if found:
        print(f"\n BANNED PHRASES FOUND: {found}")
    else:
        print("\n No banned phrases detected")