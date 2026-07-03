from medmate.agent.tools.database import add_medication_db, remove_medication_db, list_medications_db
import logging

logger = logging.getLogger(__name__)

def add_medication(name: str, dose: str, frequency: str, start_date: str, end_date: str = None, notes: str = None) -> str:
    """
    Adds or updates a medication in the user's active medication list.

    Args:
        name: Name of the medication (e.g., 'lisinopril', 'ibuprofen').
        dose: The dose/strength (e.g., '10mg', '400mg').
        frequency: How often it is taken (e.g., 'once daily', 'twice a day').
        start_date: Start date for the medication in YYYY-MM-DD format.
        end_date: Optional end date in YYYY-MM-DD format.
        notes: Optional additional instructions or notes.
    """
    success = add_medication_db(name, dose, frequency, start_date, end_date, notes)
    if success:
        return f"Medication '{name}' ({dose}) has been successfully saved to your list."
    else:
        return f"Error: Could not add medication '{name}' to your list."

def remove_medication(name: str) -> str:
    """
    Removes a medication and its scheduled reminders from the user's active list.

    Args:
        name: Name of the medication to remove.
    """
    success = remove_medication_db(name)
    if success:
        return f"Medication '{name}' and all associated reminders have been successfully removed."
    else:
        return f"Error: Could not remove medication '{name}' from your list."

def list_medications() -> str:
    """
    Retrieves and lists all medications currently in the active medication list.
    """
    meds = list_medications_db()
    if not meds:
        return "You currently have no medications in your list."
    
    output = "Here are your current medications:\n"
    for med in meds:
        end_date_str = f", End Date: {med['end_date']}" if med['end_date'] else ""
        notes_str = f" (Notes: {med['notes']})" if med['notes'] else ""
        output += f"- {med['name'].capitalize()}: {med['dose']} taken {med['frequency']} starting {med['start_date']}{end_date_str}{notes_str}\n"
    return output
