import requests
import json
import os
import logging
import re

logger = logging.getLogger(__name__)

# Load fallback database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FALLBACK_PATH = os.path.join(BASE_DIR, 'data', 'sample_medications.json')

def check_openfda_pair(drug_a: str, drug_b: str) -> dict:
    """Queries the openFDA API for interactions between two drugs."""
    try:
        # Search for drug_a generic name and drug_b in the interactions section
        params = {
            "search": f'openfda.generic_name:"{drug_a}" AND drug_interactions:"{drug_b}"',
            "limit": 1
        }
        url = "https://api.fda.gov/drug/label.json"
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                interactions_list = results[0].get("drug_interactions", [])
                if interactions_list:
                    # Find paragraph or sentence containing the second drug name
                    full_text = " ".join(interactions_list)
                    
                    # Highlight or extract relevant sentence
                    matching_sentences = []
                    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', full_text)
                    for sentence in sentences:
                        if drug_b.lower() in sentence.lower():
                            matching_sentences.append(sentence.strip())
                            
                    description = " ".join(matching_sentences[:3]) if matching_sentences else full_text[:400] + "..."
                    
                    # Determine severity based on warnings keywords
                    severity = "Moderate"
                    text_lower = full_text.lower()
                    if "contraindicated" in text_lower or "fatal" in text_lower or "never" in text_lower:
                        severity = "Critical"
                    elif "severe" in text_lower or "avoid" in text_lower or "serious" in text_lower:
                        severity = "Severe"
                        
                    return {
                        "drug1": drug_a,
                        "drug2": drug_b,
                        "severity": severity,
                        "description": description,
                        "advice": "Consult your doctor or pharmacist immediately regarding this co-administration warning."
                    }
        elif response.status_code >= 500:
            # Server error, trigger local fallback
            raise requests.exceptions.RequestException("openFDA Server Error")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error querying openFDA: {e}")
        # Raise to trigger fallback logic
        raise e
    except Exception as e:
        logger.error(f"Error checking openFDA pair: {e}")
        
    return None

def check_interactions_api(medications: list) -> list:
    """Checks interactions between a list of drugs using the openFDA Drug Labeling API."""
    interactions = []
    meds_clean = [m.strip().lower() for m in medications]
    
    # Check all pairs in the list
    for i in range(len(meds_clean)):
        for j in range(i + 1, len(meds_clean)):
            m1 = meds_clean[i]
            m2 = meds_clean[j]
            
            try:
                # Try drug1 generic name with drug2 interaction
                res = check_openfda_pair(m1, m2)
                if not res:
                    # Try drug2 generic name with drug1 interaction
                    res = check_openfda_pair(m2, m1)
                    
                if res:
                    interactions.append(res)
            except Exception as e:
                # Network or server issues raise to parent to trigger local fallback
                raise e
                
    return interactions

def check_interactions_local(medications: list) -> list:
    """Checks interactions against the local fallback JSON database."""
    interactions = []
    meds_lower = [m.strip().lower() for m in medications]
    
    try:
        if os.path.exists(FALLBACK_PATH):
            with open(FALLBACK_PATH, 'r', encoding='utf-8') as f:
                fallback_data = json.load(f)
            
            # Check all pairs in the input list
            for i in range(len(meds_lower)):
                for j in range(i + 1, len(meds_lower)):
                    m1 = meds_lower[i]
                    m2 = meds_lower[j]
                    
                    for interaction in fallback_data:
                        d1 = interaction["drug1"].lower()
                        d2 = interaction["drug2"].lower()
                        
                        if (m1 in d1 and m2 in d2) or (m2 in d1 and m1 in d2):
                            interactions.append({
                                "drug1": m1,
                                "drug2": m2,
                                "severity": interaction["severity"],
                                "description": interaction["description"],
                                "advice": interaction["advice"]
                            })
    except Exception as e:
        logger.error(f"Error checking local interactions: {e}")
        
    return interactions

def check_interactions(medications: list) -> str:
    """
    Checks for potential drug-drug interactions among the list of medications provided.
    
    Args:
        medications: A list of drug names (e.g., ['aspirin', 'warfarin']).
    """
    if not medications or len(medications) < 2:
        return "Please specify at least two medications to check for interactions."

    interactions = []
    api_failed = False
    
    logger.info(f"Checking interactions online via openFDA for: {medications}")
    try:
        interactions = check_interactions_api(medications)
    except Exception as e:
        logger.warning(f"openFDA API failed ({e}). Falling back to local interaction database...")
        api_failed = True
        
    # If API failed, or we couldn't resolve online interactions, use local fallback
    if api_failed or not interactions:
        interactions = check_interactions_local(medications)
        
    if not interactions:
        return f"No documented interactions found between the medications: {', '.join(medications)}."
    
    result = "### Potential Drug Interactions Detected\n\n"
    for item in interactions:
        severity = item['severity']
        severity_label = f"**[{severity.upper()}]**"
        
        result += f"- **{item['drug1'].capitalize()}** and **{item['drug2'].capitalize()}**:\n"
        result += f"  - **Severity**: {severity_label}\n"
        result += f"  - **Description**: {item['description']}\n"
        result += f"  - **Advice**: *{item['advice']}*\n\n"
        
    result += "\n**Disclaimer**: This interaction check is powered by openFDA live drug labels and fallback lists. "
    result += "It does not replace professional medical advice. Always consult a doctor or pharmacist."
    return result
