# Member 3 — Job Matching + RAG Pipeline + Skill Gap Detection

**Owner:** Member 3 - Priyanshi Saini
**Files owned:** `agent/agent_jobs.py`, `task/task_match_jobs.py`, `tool/tool_jsearch.py`, `tool/tool_rag_pipeline.py`, `data/rawFolder/`, `data/processed/`

This module is the only true RAG pipeline in the project — it retrieves job listings by **semantic similarity over a vector store**, then hands the retrieved results to an LLM for reasoning.

---

## 1. RAG vs. Tool-Augmented Generation

These are often confused, so it's worth being precise:

- **Tool-augmented generation** is calling an external API (e.g. JSearch) and passing whatever it returns straight into an LLM prompt. There's no retrieval step — no embeddings, no similarity search, no vector store. The LLM just reasons over raw API output.
- **RAG (Retrieval-Augmented Generation)** adds a retrieval layer *before* generation: text is converted into embeddings, stored in a vector database, and at query time the query is embedded with the **same model** and compared against stored vectors using similarity search. Only the top-k most relevant results are passed to the LLM.

This pipeline is genuine RAG because job descriptions are embedded and stored in ChromaDB, and retrieval happens via **cosine similarity search** over that vector store — not just a raw API call fed into a prompt. Fetching jobs from JSearch (tool-augmented step) and retrieving them semantically (RAG step) are two distinct stages in this pipeline, and it's important not to conflate them.

---

## 2. The 6-Step Pipeline

| Step | File | What happens |
|------|------|---------------|
| **1. Fetch raw jobs** | `tool_jsearch.py` | Calls the JSearch API for the target role, caches results, and saves the raw response to `data/rawFolder/cache_{role}.json`. |
| **2. Embed job descriptions** | `tool_rag_pipeline.py` | Each job listing (`title + company + description`) is encoded into a vector using `all-MiniLM-L6-v2`, the same embedding model M2 uses for the resume. |
| **3. Store in ChromaDB** | `tool_rag_pipeline.py` | Embeddings, along with metadata (title, company) and the original text, are written to a ChromaDB `PersistentClient` collection persisted at `data/processed/`. |
| **4. Embed the query** | `tool_rag_pipeline.py` | The user's skill/resume query is embedded — in practice, this reuses `state["resume_embedding"]` produced upstream by M2, so the resume never needs to be re-embedded. |
| **5. Semantic similarity search** | `tool_rag_pipeline.py` | The query embedding is compared against all stored job embeddings via cosine similarity; the top-5 most similar jobs are retrieved. |
| **6. LLM reasoning over retrieved chunks** | `task_match_jobs.py` | The top-k retrieved jobs are passed to the LLM, which returns structured JSON per job: `match_score`, `matched_skills`, and `missing_skills`. |

**Why this matters for skill gaps:** `missing_skills` returned in Step 6 is aggregated across the top matches to populate `state["skill_gaps"]`, which Member 4 uses to build the learning roadmap.

---

## 3. What `all-MiniLM-L6-v2` Produces

`all-MiniLM-L6-v2` is a sentence-transformer model that maps any input text (a job description or a resume) to a fixed-length **384-dimensional dense vector**. Semantically similar texts — even if worded differently — end up close together in this 384-dimensional space, which is what makes similarity search meaningful.

This is the exact contract shared with Member 2:

- `EMBEDDING_MODEL = "all-MiniLM-L6-v2"` is defined once in `graph/state.py` and imported by both M2 and M3.
- M2 embeds the resume → `state["resume_embedding"]`.
- M3 embeds every job description with the **same model** and uses the resume embedding as the query vector.

**Why the model must match on both sides:** cosine similarity only makes sense when both vectors were produced by the same model in the same embedding space. If the resume were embedded with a different model than the job listings, the similarity scores would be comparing two unrelated coordinate systems — the numbers would still come out, but they'd be meaningless.

---

## 4. Where Data Lives

| Location | Contents |
|----------|----------|
| `data/rawFolder/` | Raw, unprocessed JSearch API responses — e.g. `cache_{role}.json`, `sample_jobs.json`. This is the offline/dev cache that lets the pipeline be tested without repeatedly hitting the API (important given JSearch's free-tier limit of 200 requests/month). |
| `data/processed/` | ChromaDB's `PersistentClient` storage path. This holds the actual vector index — embeddings, metadata, and document text for every embedded job listing — and persists across runs so jobs don't need to be re-embedded every time. |

The split mirrors the pipeline itself: `rawFolder/` is pre-embedding (Step 1 output), `processed/` is post-embedding (Step 2–3 output).

**Edge case:** if `data/processed/` is empty (e.g. no jobs embedded yet) and a query is run, `collection.query()` on an empty ChromaDB collection returns no results rather than erroring — so the pipeline should check for an empty result set before passing it to `task_match_jobs.py`, otherwise the LLM reasoning step gets an empty context.

---

## 5. How Retrieval Quality Was Evaluated

Since there's no labeled job-relevance dataset for this project, evaluation was done manually and qualitatively rather than with an automated metric:

1. **Spot-check retrieval against known resumes.** For a resume with a clear target role (e.g. "Software Engineer Intern" with Python/SQL skills), the top-5 retrieved jobs were manually inspected to confirm they were plausible matches for that role — not random or off-topic listings.
2. **Keyword sanity check.** Retrieved job titles/descriptions were checked for expected keyword overlap with the resume's skills (e.g. a Python-heavy resume should surface backend/data roles, not, say, purely design roles), as a rough proxy for relevance without needing formal precision/recall labels.
3. **Compared semantic vs. naive matching.** Queries with paraphrased skill terms (e.g. "built REST APIs" vs. a job description saying "backend development") were used to confirm the pipeline retrieves relevant jobs even without exact keyword overlap — the point of semantic over keyword search.
4. **Score distribution check.** Cosine similarity scores across retrieved results were checked to make sure they weren't clustering near zero (which would signal noisy/irrelevant embeddings) or all identical (which would signal a broken/empty collection returning arbitrary order).

**Honest limitation:** this is manual, small-scale evaluation (a handful of test resumes), not a formal metric like precision@k over a labeled ground-truth set. That's a reasonable next step if the project were extended, but wasn't in scope given the timeline.

---
