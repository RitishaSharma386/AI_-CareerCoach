# Member 4 – Roadmap & Cover Letter Agent

## Overview

This module generates two career-prep deliverables: a personalized 4-week learning roadmap
based on the user's skill gaps, and a tailored cover letter based on the user's resume and
a target job listing.

It uses OpenRouter for generation and integrates into the shared LangGraph workflow as two
separate nodes: `roadmap` and `cover_letter`.

---

## Components

- OpenRouter (Generation)
- Shared AgentState
- `task/task_generate_roadmap.py`
- `task/task_generate_cover_letter.py`
- `agent/agent_roadmap.py`
- `agent/agent_cover_letter.py`

---

## AgentState Fields Used

| Field | Direction | Notes |
|-------|-----------|-------|
| `target_role` | Read | Required for roadmap generation |
| `skill_gaps` | Read | Required for roadmap generation |
| `resume_json` | Read | Required for cover letter generation |
| `job_listings` | Read | First listing is used for cover letter generation |
| `roadmap` | Write | Output of roadmap node |
| `cover_letter` | Write | Output of cover letter node |
| `error` | Write | Set on any failure or guard rejection |

---

## Guard Conditions

**Roadmap agent (`agent_roadmap.py`):**
- If `skill_gaps` is empty → skips generation, returns
  `{"roadmap": "Your profile already matches this role well!"}` (treated as a valid
  outcome, not an error).
- If `target_role` is missing → returns `{"roadmap": None, "error": "Missing target_role in state"}`.

**Cover letter agent (`agent_cover_letter.py`):**
- If `resume_json` or `job_listings` is missing/empty → returns
  `{"cover_letter": None, "error": "Missing resume_json or job_listings in state"}`.
- If `job_description` is under 50 words → skips generation, returns
  `{"cover_letter": None, "error": "Job description too short to generate a meaningful cover letter."}`.
  This guard is load-bearing: `graph.py` currently routes unconditionally from
  `roadmap → cover_letter`, so a `get_roadmap`-only request would otherwise reach the
  cover letter node with empty job data. Flagged to Member 1 — the routing table in
  `member1_orchestrator.md` implies `get_roadmap` terminates after the roadmap node, but
  the actual graph code continues into `cover_letter` regardless of intent.

Both agents wrap their LLM call in try/except so a failure never crashes the graph — it's
captured in `state["error"]` instead, consistent with the orchestrator's error-handling pattern.

---

## Model Configuration

- **Model:** `openai/gpt-oss-20b:free` (same provider used by the orchestrator's intent classifier)
- **Temperature:** `0`
- **max_tokens:** `3000`
- **Reasoning effort:** `low` (via `extra_body={"reasoning": {"effort": "low"}}`)
- **Retry logic:** up to 2 attempts per call if the LLM returns an empty response
- **Empty-response guard:** raises `ValueError` after retries are exhausted, so it surfaces
  as a catchable `error` in state rather than silently returning `None`

### Why this configuration

Three different free-tier setups were tried during testing — `openrouter/free` (auto-router),
`meta-llama/llama-3.3-70b-instruct:free`, and `openai/gpt-oss-20b:free` at default settings —
and all three occasionally produced corrupted output: stray non-English characters, broken
grammar mid-sentence, or once a literal `"User Safety: safe"` string instead of a letter.
Pinning `temperature=0` on `gpt-oss-20b:free` eliminated corruption across repeated test runs.

A second, separate failure mode was then found: calls would occasionally return
`content: None` with no exception raised. Inspecting the full response object
(`tests/debug_empty_response.py`) showed the root cause — `gpt-oss-20b` is a **reasoning
model** that spends part of its `completion_tokens` budget on an internal reasoning pass
before writing the visible answer (e.g. one call used 251 of 268 total completion tokens on
reasoning alone). On long, structured prompts (roadmap/cover letter), the reasoning pass can
consume the entire token budget, leaving nothing for the actual output. Raising `max_tokens`
to 3000 and setting `reasoning.effort` to `"low"` reduced this significantly; the retry loop
covers the residual cases.

**Consistency note:** even at `temperature=0`, 3 identical-input runs of the roadmap task
produced 2 identical outputs and 1 meaningfully divergent one (different formatting, different
named platforms). Temperature=0 reduces but does not guarantee deterministic output on this
model/provider — worth knowing if exact reproducibility is ever assumed elsewhere in the project.

---

## Testing Performed

- **Unit tests (`tests/test_agents.py`):** normal input, empty `skill_gaps`, short
  `job_description`, missing `job_listings` — all passing.
- **Unit tests (`tests/test_task_roadmap.py`, `tests/test_task_cover_letter.py`):** direct
  tests of the LLM-calling functions (return type, word count, banned phrases,
  greeting/sign-off structure, no URLs). Cover letter tests fully passing; roadmap tests
  passing on retry (one assertion on week-label formatting needs a more flexible match —
  known minor issue, not a generation failure).
- **Manual eval (`tests/eval_roadmap.py`):** 5 varied skill-gap lists (SWE Intern, Data
  Scientist, Frontend Dev, DevOps, AI Engineer). Content is genuinely specific per role, not
  templated with swapped nouns. Zero hallucinated URLs (regex-checked).
- **Manual eval (`tests/eval_cover_letter.py`):** 5 varied job listings (Google, Amazon,
  Microsoft, Meta, FinTrust). Zero banned phrases ("I am passionate about", "team player",
  "hard worker"), zero fabricated technologies/metrics after prompt tightening, zero
  corrupted output on the final model config.
- **Consistency check (`tests/consistency_check.py`):** 3 identical-input runs — see note above.
- **End-to-end graph test (`graph/graph.py`):** confirmed error propagation works correctly
  when an upstream node fails (tested against `agent_resume.py` missing a `run()` function —
  caught cleanly via `state["error"]` instead of crashing the graph).

---

## Prompt Iteration Notes

The cover letter prompt was tightened twice during testing:
1. Added an instruction against inventing specific technologies, metrics, or achievements not
   present in the input resume — an early version fabricated a "30% task-completion time"
   improvement and invented tools like Kubernetes/PyTorch that weren't in the resume.
2. Broadened the "don't start with 'I am writing to apply'" instruction to cover generic
   variants like "I am excited to apply/submit", since the model was initially working around
   the literal banned string rather than avoiding the pattern.

**Known limitation:** with a resume containing only a project name and a short skill list (no
project description), the model has only one real fact to draw from, producing letters that
repeat the same project mention 2–3 times across paragraphs. This is a resume-input richness
limitation, not a prompt bug — flagged to whoever owns resume parsing as a potential
improvement (richer `resume_json` → richer letters).

---

## Known Issues / Tradeoffs

- **Free-tier reliability:** OpenRouter free models can rate-limit or occasionally return
  corrupted/empty output under load, independent of model choice. Mitigated via
  `temperature=0`, low reasoning effort, higher `max_tokens`, and a 2-attempt retry — not
  fully eliminated.
- **Thin resume input → repetitive letters** (see above).
- **Routing assumption mismatch:** `graph.py`'s unconditional `roadmap → cover_letter` edge
  doesn't match the intent-routing table described in `member1_orchestrator.md`. The 50-word
  job-description guard currently absorbs this, but the underlying routing logic may need
  review by Member 1.
- **`data/processed/chroma.sqlite3`** (and related binary vector-store files) caused an
  unmergeable Git conflict during a `dev` pull, since Git can't line-merge binary files.
  Resolved by taking the incoming version (`--theirs`). Recommend adding
  `data/processed/` to `.gitignore` so generated/binary pipeline output stops causing repeat
  merge conflicts — worth raising with whoever owns the RAG pipeline.

---

## Technologies

- Python
- OpenAI SDK (OpenRouter-compatible)
- LangGraph (node integration)