"""
File: tests/final_eval.py
Owner: Member 4 — Shraddha Tyagi
Function: Runs agent_roadmap and agent_cover_letter 5x each on varied mock
          states, for manual best/worst review before final submission.
"""
from agent import agent_roadmap, agent_cover_letter

roadmap_states = [
    {"target_role": "Software Engineer Intern", "skill_gaps": ["Docker", "System Design", "SQL"]},
    {"target_role": "Data Scientist", "skill_gaps": ["Pandas", "Statistics", "Machine Learning"]},
    {"target_role": "Frontend Developer", "skill_gaps": ["React", "CSS", "TypeScript"]},
    {"target_role": "DevOps Engineer", "skill_gaps": ["Kubernetes", "CI/CD", "AWS"]},
    {"target_role": "AI Engineer", "skill_gaps": ["LangChain", "Prompt Engineering", "Vector Databases"]},
]

cover_letter_states = [
    {
        "resume_json": {"name": "Riya", "skills": ["Agentic AI", "Gen AI", "Data Science"], "projects": ["Agentic AI Productivity Tracker"]},
        "job_listings": [{"company": "Google", "job_title": "AI Engineer", "job_description": "Work on Gemini model infrastructure and scalable machine learning systems that serve millions of users worldwide. "
        "This role requires strong Python programming skills, hands-on experience with distributed systems, and deep familiarity with large-scale data pipelines,"
        " model serving infrastructure, and production AI workloads across global data centers and diverse hardware environments,"
        " while collaborating closely with research teams on model reliability."}],
    },
    {
        "resume_json": {"name": "Riya", "skills": ["Agentic AI", "Gen AI", "Data Science"], "projects": ["Agentic AI Productivity Tracker"]},
        "job_listings": [{"company": "Amazon", "job_title": "SDE Intern", "job_description": "Build backend services for the retail platform using Java and AWS."
        " Requires knowledge of data structures, algorithms, distributed systems, and experience with cloud infrastructure and microservices architecture at scale."
        "Candidates should be comfortable working in a fast-paced environment with frequent deployments and cross-functional collaboration across engineering teams, "
        "and should be eager to learn new tools quickly on the job."}],
    },
    {
        "resume_json": {"name": "Riya", "skills": ["Agentic AI", "Gen AI", "Data Science"], "projects": ["Agentic AI Productivity Tracker"]},
        "job_listings": [{"company": "Microsoft", "job_title": "Data Scientist", "job_description": "Analyze large datasets to drive product decisions across Azure services."
        " Requires strong SQL, Python, statistics background, and experience building and deploying machine learning models in production environments. The ideal candidate is comfortable communicating technical findings to both engineering and non-technical stakeholders,"
        " and enjoys working cross-functionally with product managers to translate data into strategy."}],
    },
    {
        "resume_json": {"name": "Riya", "skills": ["Agentic AI", "Gen AI", "Data Science"], "projects": ["Agentic AI Productivity Tracker"]},
        "job_listings": [{"company": "Meta", "job_title": "ML Engineer", "job_description": "Design and deploy recommendation systems for billions of users. Requires deep learning experience, familiarity with PyTorch or TensorFlow,"
        " and strong understanding of distributed training and model optimization techniques. Experience with large-scale data infrastructure and A/B testing is a strong plus for this role, along with a track record of shipping production ML systems at scale."}],
    },
    {
        "resume_json": {"name": "Riya", "skills": ["Agentic AI", "Gen AI", "Data Science"], "projects": ["Agentic AI Productivity Tracker"]},
        "job_listings": [{"company": "FinTrust", "job_title": "Backend Developer", "job_description": "Build secure, scalable APIs for a fast-growing fintech product."
        " Requires Node.js or Python, database design experience, and comfort working in a fast-paced startup environment with rapid iteration and frequent shipping of new features to production,"
        " alongside a strong emphasis on data security and regulatory compliance standards."}],
    },
]

print("\n" + "#" * 70)
print("ROADMAP AGENT — 5 RUNS")
print("#" * 70)
for i, state in enumerate(roadmap_states, 1):
    print(f"\n{'='*60}\nROADMAP RUN {i}: {state['target_role']}\n{'='*60}")
    result = agent_roadmap.run(state)
    if result.get("error"):
        print(f"⚠️  ERROR: {result['error']}")
    else:
        print(result["roadmap"])

print("\n" + "#" * 70)
print("COVER LETTER AGENT — 5 RUNS")
print("#" * 70)
for i, state in enumerate(cover_letter_states, 1):
    company = state["job_listings"][0]["company"]
    print(f"\n{'='*60}\nCOVER LETTER RUN {i}: {company}\n{'='*60}")
    result = agent_cover_letter.run(state)
    if result.get("error"):
        print(f"⚠️  ERROR: {result['error']}")
    else:
        print(result["cover_letter"])

print("\n\nDone. Review above and pick your best/worst output for each agent.")