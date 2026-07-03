# MedMate — Architecture Documentation

This document describes the design, data flow, and components of the MedMate Concierge Agent.

## Overview

MedMate is a secure, client-facing healthcare utility. It is designed to act as a bridge between patient inputs, deterministic relational databases, public drug knowledge bases (RxNav), and large language models (Gemini).

```
+-----------------------------------------------------------+
|                       Streamlit UI                        |
|   (Interactive tabs for Chat, Manual Forms, Checkers)    |
+-----------------------------+-----------------------------+
                              | User input / actions
                              v
+-----------------------------------------------------------+
|                       Root Agent                          |
|  - Pre-execution prompt injection defense                  |
|  - Google ADK model runner orchestrator                   |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
|                     Google ADK Engine                     |
|  - Selects matching skill (check_interactions, etc.)      |
|  - Routes to deterministic Python tool functions           |
+-----------------------------+-----------------------------+
                              |
              +---------------+---------------+
              |                               |
              v                               v
+-----------------------------+ +-----------------------------+
|    External Web Services    | |      Local Data Store       |
|  - RxNav API (online check) | |  - SQLite (meds/reminders)  |
|  - Gemini API (summaries)   | |  - sample_medications.json  |
+-----------------------------+ +-----------------------------+
```

## Key Components

### 1. Streamlit Interface (`streamlit_app.py`)
- Employs a stateful design utilizing `st.session_state` to store conversation history and interface alerts.
- Divided into interactive tabs to separate natural language chat from structured form workflows (like manual medication input and the prescription summarizer).

### 2. Google ADK Agent Orchestration (`root_agent.py`)
- Standardizes LLM and tool connections.
- Exposes tools directly as typed Python functions, allowing the Gemini model to dynamically call them based on the task description.

### 3. Local SQLite database (`database.py`)
- Persists user medications, start/end dates, dosage details, and reminder settings.
- Enforces relational safety through cascading deletes.

### 4. RxNav Integration (`interaction_checker.py`)
- Converts medication names to RxCUIs via search API.
- Evaluates drug interactions using RxNav REST interface, defaulting to local JSON templates upon network timeout or API failures.
