# MedMate — Software Specification

## Problem Statement
Managing medications safely is a major challenge for patients, especially those on multiple prescriptions. Drug-drug interactions, scheduling errors, and complex medical jargon lead to poor adherence and severe health hazards. Patients need a secure, private, and clear health concierge to help them track their medication lists, understand their prescriptions, flag potential drug interactions, and receive reminders.

## Target Users
- **Patients with Chronic Conditions**: Individuals managing multiple medications daily.
- **Elderly Caregivers**: People assisting family members with daily pill regimens.
- **Health-Conscious Individuals**: Anyone seeking to check potential drug interactions and simplify prescription instructions.

## Goals
- **Medication Management**: Provide an easy way to log, view, and remove medications.
- **Safety Checker**: Detect drug-drug interactions automatically using RxNav/openFDA API with a local fallback dataset.
- **Scheduler**: Schedule clear, time-based reminders for pill intake.
- **Prescription Simplification**: Summarize complex medical instructions into simple, friendly language.
- **Privacy & Security**: Enforce data privacy, prevent prompt injection, protect against SQL injection, and refuse unsafe requests.

## Out of Scope
- **Diagnosis**: MedMate will NEVER diagnose diseases or suggest medical conditions.
- **Prescribing / Dosing**: MedMate will NOT prescribe new medications or suggest custom dosages.
- **Emergency Response**: MedMate is not a life-saving emergency medical device.

## User Stories
- *As a patient*, I want to add my daily lisinopril so that I can keep an active list.
- *As a user*, I want to know if my new painkiller interacts with my blood thinner so that I can avoid dangerous side effects.
- *As a caregiver*, I want to set a reminder at 8:00 AM for insulin intake so that it is never missed.
- *As a non-native English speaker*, I want to simplify my doctor's instructions so that I understand exactly when and how to take my pills.

## Functional Requirements
1. **Medication Management**:
   - `add_medication`: Save name, dose, frequency, start date, end date, and notes to SQLite.
   - `remove_medication`: Remove selected drug from list.
   - `list_medications`: Query and display current medications.
2. **Drug Interaction Checker**:
   - `check_interactions`: Take list of drugs, call RxNav REST API. If API fails, query `sample_medications.json`.
   - Clear rating (Critical, Severe, Moderate, Info) and simple plain-language explanations.
3. **Prescription Summarizer**:
   - `summarize_prescription`: Accept raw text, return structured Markdown with Medication, Purpose, Frequency, Warnings, and a simplified explanation.
4. **Reminder Scheduler**:
   - `schedule_reminder`: Store reminder schedule in SQLite, show upcoming alerts in Streamlit.
5. **Secure Prompt Guard**:
   - Reject prompt injection attacks (e.g., instructions to reveal system prompts, bypass safety, delete database, run shell commands).
   - Refuse medical diagnosis or custom dosage recommendations, directing the user to consult doctors.

## Non-functional Requirements
- **Security**: Parameterized SQL queries to block SQL injection; markdown sanitization; prompt injection filtering; safe environment variable loading.
- **Performance**: Under 2-second response times for typical agent requests.
- **Usability**: Clean, modern, responsive Streamlit UI with sidebar and tabs.

## Architecture
- **Frontend**: Streamlit UI (Sidebar: lists + reminders; Main: Chat, Forms).
- **Orchestration**: Google ADK Root Agent with Gemini 2.5 Flash.
- **Storage**: SQLite database (`medmate.db`) for medications & reminders.
- **External Integration**: RxNav API via HTTP requests.

## Security
- **Strict Delimiters**: Instructions and user content separated by safe wrappers.
- **PII Minimization**: Store only drug name, dose, frequency, start date, notes.
- **Input Sanitization**: Block executable python code/SQL keywords.
- **No Unsafe Code**: Avoid `eval()`, `exec()`, `pickle`.

## Evaluation Plan
- 10 test scenarios covering standard commands, edge cases, safety prompts, and malicious inputs.
- Verification script `evaluator.py` runs tests and outputs `eval/results.md`.

## Success Metrics
- 100% of SQL injection attempts blocked.
- 100% of prompt injection attempts rejected safely.
- 0 false positives/negatives in local fallback interaction matches.
- All diagnosis requests successfully redirected to medical professionals.
