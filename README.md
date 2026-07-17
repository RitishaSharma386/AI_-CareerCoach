# AI_-CareerCoach
## Member 4 – Roadmap & Cover Letter Agent (Shraddha Tyagi)

Generates two career-prep deliverables from the shared `AgentState`:

- **4-week learning roadmap** based on the user's target role and skill gaps
- **Tailored cover letter** based on the user's resume and a target job listing

### Files

| File | Purpose |
|------|---------|
| `task/task_generate_roadmap.py` | Core LLM call that generates the roadmap |
| `task/task_generate_cover_letter.py` | Core LLM call that generates the cover letter |
| `agent/agent_roadmap.py` | LangGraph node wrapper — reads/writes `AgentState`, handles guards & errors |
| `agent/agent_cover_letter.py` | LangGraph node wrapper — reads/writes `AgentState`, handles guards & errors |
| `tests/test_agents.py` | Unit tests for both agent wrappers, including guard conditions |
| `tests/test_task_roadmap.py` | Unit tests for the raw roadmap generation function |
| `tests/test_task_cover_letter.py` | Unit tests for the raw cover letter generation function |
| `tests/eval_roadmap.py` | Manual eval — 5 varied roles, checks specificity & URL usage |
| `tests/eval_cover_letter.py` | Manual eval — 5 varied job listings, checks banned phrases & fabrication |
| `docs/member4_roadmap_agent.md` | Full documentation: guards, model config, testing, known issues |

### How it works

Both agents follow the same pattern: read the relevant fields from `AgentState`, run a guard
check, call OpenRouter (`openai/gpt-oss-20b:free`, `temperature=0`) with a retry on empty
responses, and return only the new key(s) they contribute (`{"roadmap": ...}` or
`{"cover_letter": ...}`) — never the full state — consistent with how the orchestrator merges
node outputs.

**Guards:**
- Empty `skill_gaps` → returns a friendly "already matches this role" message instead of calling the LLM.
- Missing `resume_json` / `job_listings`, or a `job_description` under 50 words → skips generation and sets `state["error"]` instead of crashing downstream.

See `docs/member4_roadmap_agent.md` for full details on model configuration, prompt design decisions, and known reliability tradeoffs with free-tier OpenRouter models.

### Status

✅ Both agents integrated as LangGraph nodes, guards tested, prompts evaluated on 5+ varied
inputs each. Blocked on full end-to-end testing with real (non-mock) job listing data pending
Member 3's resume/RAG pipeline output.