import requests
import json
import os
import logging

logger = logging.getLogger(__name__)

# Load fallback database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FALLBACK_PATH = os.path.join(BASE_DIR, 'data', 'sample_medications.json')

def get_rxcui(drug_name: str) -> str:
    """Fetches the RxCUI for a given drug name using the RxNav API."""
    try:
        url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            id_group = data.get("idGroup", {})
            rxnorm_ids = id_group.get("rxnormId")
            if rxnorm_ids:
                return rxnorm_ids[0]
    except Exception as e:
        logger.error(f"Error fetching RxCUI for {drug_name}: {e}")
    return None

def check_interactions_api(rxcuis: list) -> list:
    """Checks interactions between a list of RxCUIs using the RxNav API."""
    if len(rxcuis) < 2:
        return []
    
    rxcuis_str = "+".join(rxcuis)
    url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={rxcuis_str}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            interactions = []
            
            # Parse RxNav interaction response structure
            # fullInteractionTypeGroup -> fullInteractionType -> interactionPair
            type_groups = data.get("fullInteractionTypeGroup", [])
            for group in type_groups:
                for interaction_type in group.get("fullInteractionType", []):
                    for pair in interaction_type.get("interactionPair", []):
                        # Extract description and severity
                        severity = pair.get("severity", "N/A")
                        description = pair.get("description", "")
                        concepts = pair.get("interactionConcept", [])
                        
                        drugs = []
                        for concept in concepts:
                            source_concept = concept.get("minConceptItem", {})
                            drugs.append(source_concept.get("name", "Unknown Drug"))
                        
                        interactions.append({
                            "drug1": drugs[0] if len(drugs) > 0 else "Unknown",
                            "drug2": drugs[1] if len(drugs) > 1 else "Unknown",
                            "severity": severity,
                            "description": description,
                            "advice": "Consult your healthcare provider regarding the use of these medications together."
                        })
            return interactions
    except Exception as e:
        logger.error(f"Error checking interactions via RxNav: {e}")
    return []

def check_interactions_local(medications: list) -> list:
    """Checks interactions against the local fallback JSON database."""
    interactions = []
    meds_lower = [m.strip().lower() for m in medications]
    
    try:
        if os.path.exists(FALLBACK_PATH):
            with open(FALLBACK_PATH, 'r') as f:
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

    # Try API first
    logger.info(f"Checking interactions online for: {medications}")
    rxcuis = []
    unresolved = []
    
    for med in medications:
        rxcui = get_rxcui(med)
        if rxcui:
            rxcuis.append(rxcui)
        else:
            unresolved.append(med)
            
    interactions = []
    api_failed = False
    
    if len(rxcuis) >= 2:
        try:
            interactions = check_interactions_api(rxcuis)
        except Exception:
            api_failed = True
    else:
        api_failed = True
        
    # If API failed, or we couldn't resolve RxCUIs, use local fallback
    if api_failed or not interactions:
        logger.info("Falling back to local interaction database...")
        interactions = check_interactions_local(medications)
        
    if not interactions:
        return f"No documented interactions found between the medications: {', '.join(medications)}."
    
    result = "### Potential Drug Interactions Detected\n\n"
    for item in interactions:
        severity = item['severity']
        severity_label = f"**[{severity.upper()}]**"
        
        # Color coding severity indicator in markdown using standard bold/italics
        result += f"- **{item['drug1'].capitalize()}** and **{item['drug2'].capitalize()}**:\n"
        result += f"  - **Severity**: {severity_label}\n"
        result += f"  - **Description**: {item['description']}\n"
        result += f"  - **Advice**: *{item['advice']}*\n\n"
        
    result += "\n**Disclaimer**: This interaction check is powered by RxNav / openFDA data and fallback lists. "
    result += "It does not replace professional medical advice. Always consult a doctor or pharmacist."
    return result
