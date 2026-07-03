---
name: summarize_prescription
description: Summarize raw prescription text. Use this skill when the user inputs a doctor's prescription text or labels and wants a simplified summary.
---

# Summarize Prescription Skill

## Goal
To extract key information from raw prescription instructions and summarize them in simple terms.

## Instructions
1. Extract the raw prescription text.
2. Call the `summarize_prescription` tool.
3. Present the resulting Markdown block.
4. Highlight important warnings, food requirements, or dosage guidelines in a structured table or bold text.
5. Remind the user to consult their pharmacist or physician.
