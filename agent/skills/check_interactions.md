---
name: check_interactions
description: Detect drug-drug interactions between medications. Use this skill when the user wants to check if multiple drugs can be taken together safely.
---

# Check Interactions Skill

## Goal
To safely check potential drug-drug interactions between two or more medications and present clear explanations.

## Instructions
1. Extract all medication names from the user input.
2. Call the `check_interactions` tool passing the list of medication names.
3. Interpret the result:
   - Identify critical or severe warnings.
   - Explain the interaction in plain, non-technical language.
4. If a severe or critical interaction is found, explicitly advise the user to contact a healthcare professional before taking them.
5. Provide a standard disclaimer.
