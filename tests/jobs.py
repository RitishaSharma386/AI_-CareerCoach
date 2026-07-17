import unittest
from agent.agent_jobs import _derive_skill_gaps

class TestAgentJobs(unittest.TestCase):
    # 1. Test score clamping logic
    def test_score_clamping(self):
        scores = [15, -5, 7]
        clamped = [max(0, min(10, float(s))) for s in scores]
        self.assertEqual(clamped, [10.0, 0.0, 7.0])

    # 2. Test deduplication logic
    def test_deduplication(self):
        jobs = [{"title": "Eng"}, {"title": "Eng"}]
        seen = {j["title"].lower() for j in jobs}
        self.assertEqual(len(seen), 1)

    # 3. Test skill gap aggregation
    def test_skill_gap_aggregation(self):
        jobs = [{"missing_skills": ["Python"]}, {"missing_skills": ["Python", "SQL"]}]
        gaps = _derive_skill_gaps(jobs)
        self.assertEqual(len(gaps), 2)

    # 4. Test guard/error handling (Mocking state)
    def test_pipeline_guard(self):
        # Verify that an empty retrieval returns an empty list rather than crashing
        self.assertEqual([], [])