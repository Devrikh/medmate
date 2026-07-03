import os
import logging

logger = logging.getLogger(__name__)

def summarize_prescription(text: str) -> str:
    """
    Summarizes raw prescription text in simple language.
    
    Args:
        text: The raw text of the prescription (e.g., 'Lisinopril 10mg PO QD for hypertension. Take with water. Do not consume alcohol.').
    """
    if not text or not text.strip():
        return "Error: Prescription text is empty."

    # Try utilizing Gemini API via google-genai
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            logger.info("Summarizing prescription using Gemini API...")
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are a medical summarization assistant. Summarize the following prescription text in simple, clear, layperson language.
            Follow this exact template:
            
            ### Prescription Summary
            - **Medication Name & Strength**: [Name and strength]
            - **Purpose**: [What is this medication for?]
            - **Instructions & Frequency**: [How and when to take it]
            - **Warnings & Safety Guidelines**: [Important safety info or side effects to watch out for]
            
            **Simple Explanation**: [A warm, simple explanation of how to use this medicine]
            
            Rules:
            1. Never recommend dosage.
            2. Never prescribe or diagnose.
            3. Always end with a disclaimer: "Please consult your doctor or pharmacist if you have any questions or concern."
            
            Prescription Text:
            "{text}"
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to summarize prescription with Gemini: {e}")
            
    # Local fallback parser
    logger.info("Using local fallback parser for prescription summary...")
    return f"""### Prescription Summary (Fallback Parsing Mode)
- **Raw Input**: {text}
- **Advice**: Please review this prescription text carefully.
- **Safety Instructions**: Always follow the instructions written on your physical medication bottle.

**Disclaimer**: Local analysis performed. Please consult your physician or pharmacist for professional guidance.
"""
