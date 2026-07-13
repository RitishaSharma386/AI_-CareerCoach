# Member 1 – Orchestrator

## Overview

The orchestrator is responsible for deciding which agent should execute based on the user's request.

Instead of using fixed keyword matching, the project uses an LLM (OpenRouter) to classify the user's intent.

---

## Workflow

User Query
↓
OpenRouter Intent Classifier
↓
Intent Prediction
↓
LangGraph Route
↓
Execute Agent

---

## Supported Intents

- find_jobs
- get_roadmap
- write_cover_letter
- full_analysis

---

## Routing Logic

| Intent | Next Node |
|---------|-----------|
| find_jobs | jobs |
| get_roadmap | roadmap |
| write_cover_letter | cover_letter |
| full_analysis | jobs → roadmap → cover_letter |

---

## Error Handling

If an invalid intent is returned, the workflow stores the error in `state["error"]` and routes to `END`.

---

## Fallback Mechanism

If the LLM returns an unexpected response, keyword-based routing is used as a backup.

---

## Technologies Used

- LangGraph
- OpenRouter
- GPT-OSS-20B
- Python