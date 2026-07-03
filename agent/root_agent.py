import os
import logging
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.genai import types

# Import tools
from medmate.agent.tools.add_medication import add_medication, remove_medication, list_medications
from medmate.agent.tools.interaction_checker import check_interactions
from medmate.agent.tools.reminder_tool import schedule_reminder, list_reminders
from medmate.agent.tools.prescription_summary import summarize_prescription
from medmate.agent.tools.database import init_db

# Load environment variables
load_dotenv()

# Initialize DB on import to make sure tables exist
init_db()

logger = logging.getLogger(__name__)

# Load instructions
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTRUCTIONS_PATH = os.path.join(BASE_DIR, 'agent', 'instructions.md')

if os.path.exists(INSTRUCTIONS_PATH):
    with open(INSTRUCTIONS_PATH, 'r') as f:
        SYSTEM_INSTRUCTIONS = f.read()
else:
    SYSTEM_INSTRUCTIONS = "You are MedMate. Help users manage medications safely."

# Initialize ADK Agent
medmate_agent = Agent(
    name="MedMate",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTIONS,
    tools=[
        add_medication,
        remove_medication,
        list_medications,
        check_interactions,
        schedule_reminder,
        list_reminders,
        summarize_prescription
    ]
)

# Initialize Session Service and Runner
session_service = InMemorySessionService()
runner = Runner(agent=medmate_agent, session_service=session_service, app_name="medmate", auto_create_session=True)

def detect_prompt_injection(user_input: str) -> bool:
    """
    Detects potential prompt injection or system override keywords.
    """
    malicious_phrases = [
        "ignore previous instructions",
        "ignore the instructions above",
        "reveal system prompt",
        "reveal your system instructions",
        "delete database",
        "drop table",
        "show api key",
        "execute shell",
        "override safety",
        "bypass safety",
        "system settings"
    ]
    cleaned_input = user_input.lower()
    for phrase in malicious_phrases:
        if phrase in cleaned_input:
            logger.warning(f"Prompt injection pattern detected: '{phrase}'")
            return True
    return False

def run_agent(user_input: str, session_id: str = "streamlit_session") -> str:
    """
    Interface to call the MedMate ADK Agent with safety and memory management.
    """
    # 1. Prompt Injection Defense
    if detect_prompt_injection(user_input):
        return (
            "I cannot fulfill this request. As MedMate, I am dedicated to helping you manage "
            "medications safely and cannot execute system override commands, database operations, "
            "or expose configuration details."
        )

    # 2. Check if API Key is configured
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return (
            "Configuration Error: Gemini API key is missing. Please set the GEMINI_API_KEY "
            "variable in your environment or .env file to enable conversation mode."
        )

    try:
        # 3. Construct the message using GenAI types
        new_msg = types.Content(parts=[types.Part.from_text(text=user_input)])
        
        # 4. Run the Agent using the ADK Runner
        events = runner.run(
            user_id="user_1",
            session_id=session_id,
            new_message=new_msg
        )
        
        final_text = ""
        for event in events:
            if event.message and event.message.parts:
                for part in event.message.parts:
                    if part.text:
                        final_text += part.text
                        
        if not final_text:
            return "I received your message but was unable to generate a response. Please try again."
            
        return final_text
    except Exception as e:
        logger.error(f"Error running MedMate ADK Agent: {e}")
        return f"An error occurred while communicating with the assistant. Details: {str(e)}"
