---
name: schedule_reminder
description: Schedule daily medication reminders. Use this skill when the user wants to set a reminder or alarm for when to take their pills.
---

# Schedule Reminder Skill

## Goal
To set a daily alarm or reminder for a specific medication.

## Instructions
1. Extract the medication name and the time (in HH:MM format) from the user input.
2. If the time is in 12-hour format (e.g. "8 AM", "10 PM"), convert it to 24-hour format ("08:00", "22:00").
3. Call the `schedule_reminder` tool with the medication name and formatted time.
4. Confirm success or explain the error if the medication does not exist in the active list.
