from medmate.agent.tools.database import add_reminder_db, list_reminders_db
import logging

logger = logging.getLogger(__name__)

def schedule_reminder(medication: str, reminder_time: str) -> str:
    """
    Schedules a new reminder for a medication.

    Args:
        medication: Name of the medication (e.g., 'lisinopril').
        reminder_time: Time of day to take the medication (e.g., '08:00', '22:00').
    """
    # Simple validation of time format HH:MM
    time_parts = reminder_time.split(":")
    if len(time_parts) != 2 or not (time_parts[0].isdigit() and time_parts[1].isdigit()):
        return "Error: Please specify the reminder time in HH:MM format (24-hour clock, e.g., '08:00' or '21:30')."
    
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return "Error: Invalid time values. Hour must be 0-23 and minute must be 0-59."

    success = add_reminder_db(medication, reminder_time)
    if success:
        return f"Reminder for '{medication}' has been scheduled daily at {reminder_time}."
    else:
        return f"Error: Could not schedule reminder. Ensure medication '{medication}' exists in your medication list first."

def list_reminders() -> str:
    """
    Lists all scheduled medication reminders.
    """
    reminders = list_reminders_db()
    if not reminders:
        return "You have no scheduled reminders."
    
    output = "Here are your scheduled reminders:\n"
    for r in reminders:
        output += f"- {r['medication_name'].capitalize()} at {r['reminder_time']}\n"
    return output
