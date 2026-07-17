from task.task_match_jobs import match_jobs
import json

def test_pipeline():
    # 1. Test "Unsafe" Handling
    print("Testing 'Unsafe' refusal...")
    # Simulate a scenario where the LLM returns an unsafe flag
    mock_unsafe_chunks = ["Some job data"]
    # (Temporarily patch get_model to return 'User Safety: safe')
    results = match_jobs(["Python"], mock_unsafe_chunks)
    print(f"Result for unsafe input: {results}")

    # 2. Test Scoring Clamping
    print("\nTesting Score Clamping...")
    # Mocking a valid response that exceeds 0-10
    mock_llm_output = '[{"job_title": "ML Engineer", "match_score": 15}]'
    # Use your clean function and parser logic to verify result is 10
    import json
    parsed = json.loads(mock_llm_output)
    clamped = max(0, min(10, float(parsed[0]['match_score'])))
    print(f"Clamped Score: {clamped}")

test_pipeline()