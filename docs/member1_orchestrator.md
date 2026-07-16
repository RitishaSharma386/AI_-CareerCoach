# Member 1 – Orchestrator

## Overview

The orchestrator is responsible for controlling the execution flow of the AI Career Coach.

It uses OpenRouter to classify the user's intent and LangGraph to execute the appropriate workflow.

---

## Components

- OpenRouter (Intent Classification)
- LangGraph
- Shared AgentState
- Resume Agent
- Jobs Agent
- Roadmap Agent
- Cover Letter Agent

---

## Supported Intents

- find_jobs
- get_roadmap
- write_cover_letter
- full_analysis

---

## Routing Logic

The Resume node is the entry point of the graph.

The orchestrator classifies the user's request into one of four intents.

| Intent | Workflow |
|---------|----------|
| find_jobs | Resume → Jobs |
| get_roadmap | Resume → Roadmap |
| write_cover_letter | Resume → Cover Letter |
| full_analysis | Resume → Jobs → Roadmap → Cover Letter |

---

## Conditional Routing

After the Jobs node:

- If intent is **full_analysis**, continue to Roadmap.
- Otherwise, terminate the workflow.

After the Roadmap node:

- If intent is **full_analysis**, continue to Cover Letter.
- Otherwise, terminate the workflow.

---

## Error Handling

If an error is present in AgentState:

- Graph immediately routes to END.

If OpenRouter fails:

- Keyword-based routing is used.

---

## Technologies

- Python
- LangGraph
- OpenRouter
- GPT-OSS-20B