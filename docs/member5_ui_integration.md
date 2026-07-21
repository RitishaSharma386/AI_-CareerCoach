# UI Integration & Architecture Documentation (Member 5)

## Overview
The frontend and command-line execution interfaces are built using **Streamlit** and Python. They feature an interactive 4-tab layout and a fallback CLI designed to give users on-demand control over their career preparation. To prevent Streamlit's continuous reruns from wiping data, the application utilizes `st.session_state` to maintain the shared `AgentState` across tabs.

---

## Core Integration Mechanisms

### 1. Session State Memory & State Management
Streamlit inherently resets its execution environment on every user interaction (such as clicking a button or switching tabs). To prevent data loss:
* The application initializes a global dictionary inside `st.session_state` to track the shared `AgentState`.
* Data extracted in **Tab 1 (Resume Processing)** is securely held in memory, making it instantly available for **Tab 2 (Job Search)**, **Tab 3 (Roadmap)**, and **Tab 4 (Cover Letter)** without requiring redundant processing.

### 2. Direct Intent Handling & UI Triggering
To ensure seamless communication between the Streamlit frontend and the backend graph workflow:
* **Tab 1:** Triggers the initial resume upload and parsing workflow upon file submission.
* **Tabs 2, 3, & 4:** When a user interacts with action buttons, the UI passes explicit instructions (`"jobs"`, `"roadmap"`, or `"cover_letter"`) directly into the state to dictate execution flow.

### 3. Execution Bypasses & Performance Optimization
To save API tokens and prevent UI freezes, the frontend coordinates with the backend state-checking logic:
* If `resume_json` already exists within the shared state, the workflow skips the expensive initial resume extraction node entirely.
* This allows the UI to instantly trigger the Jobs, Roadmap, or Cover Letter agents on demand as soon as a user clicks their respective tab buttons.

---

## Technical File Structure & Responsibilities

| File Path | Module Responsibility |
| :--- | :--- |
| `ui/app.py` | Main Streamlit application containing the 4-tab layout, session state handlers, file uploaders, and UI trigger buttons. |
| `main.py` | Command-Line Interface (CLI) application allowing developers to test the full pipeline, text ingestion, and graph invocation directly from the terminal. |

---

## Known Limitations & Future Enhancements
* **Session Persistence:** State is currently tied to the active Streamlit browser session. Refreshing the browser window clears the session state, requiring a re-upload of the resume.
* **Asynchronous Loading:** Future iterations can implement asynchronous spinners or streaming tokens to further optimize the user experience during heavy API calls (e.g., JSearch fetching).