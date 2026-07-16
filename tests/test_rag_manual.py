"""
Manual test script for tool/tool_rag_pipeline.py
Run with: python -m test_rag_manual
(Does NOT trigger tool_rag_pipeline.py's own __main__ block — that only
runs when tool_rag_pipeline.py is executed directly.)
"""
import sys
import os
# This adds the parent directory (AI_-CareerCoach) to the search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool.tool_rag_pipeline import embed_and_store, retrieve_top_k, _get_encoder


mock_jobs = [
    {
        "job_title": "Backend Developer",
        "employer_name": "Microsoft",
        "job_description": "Build scalable APIs using Python and FastAPI.",
        "job_city": "Pune",
    },
    {
        "job_title": "ML Engineer",
        "employer_name": "Meta",
        "job_description": "Train and deploy machine learning models at scale.",
        "job_city": "Bangalore",
    },
]

stored_count = embed_and_store(mock_jobs)
print(f"Stored: {stored_count} jobs")

encoder = _get_encoder()
query_vec = encoder.encode("Python API developer looking for backend roles").tolist()

top_chunks = retrieve_top_k(query_vec, k=2)
print("\nTop retrieved chunks:")
for chunk in top_chunks:
    print("---")
    print(chunk)