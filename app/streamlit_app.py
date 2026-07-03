import streamlit as st
import sys
import os

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from medmate.agent.root_agent import run_agent
from medmate.agent.tools.database import list_medications_db, list_reminders_db, add_medication_db, remove_medication_db, add_reminder_db
from medmate.agent.tools.interaction_checker import check_interactions
from medmate.agent.tools.prescription_summary import summarize_prescription

st.set_page_config(
    page_title="MedMate — Secure Personal Health Concierge",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Harmonious Teal/Emerald & Sleek Dark theme vibes)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sleek gradient top border */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* Header Gradient styling */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #10b981, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    
    /* Premium glassmorphism container cards */
    .card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .med-card {
        border-left: 4px solid #10b981;
    }
    
    .reminder-card {
        border-left: 4px solid #3b82f6;
        padding: 0.8rem 1.2rem;
    }
    
    /* Styled buttons and interactive components */
    .stButton>button {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669, #047857);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Disclaimers */
    .medical-disclaimer {
        font-size: 0.85rem;
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.2);
        background-color: rgba(239, 68, 68, 0.05);
        border-radius: 8px;
        padding: 0.8rem;
        margin-top: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE SETUP -----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "status_message" not in st.session_state:
    st.session_state.status_message = None

def clear_status():
    st.session_state.status_message = None

# Helper to render status alerts
def render_status():
    if st.session_state.status_message:
        alert_type, msg = st.session_state.status_message
        if alert_type == "success":
            st.success(msg)
        elif alert_type == "error":
            st.error(msg)
        elif alert_type == "warning":
            st.warning(msg)
        # Clear once displayed or provide a button
        st.button("Dismiss Status", on_click=clear_status, key="dismiss_status")

# ----------------- SIDEBAR CONTENT -----------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/medical-doctor.png", width=70)
    st.markdown("### 🏥 MedMate Concierge")
    st.markdown("Your secure medication organizer and interaction checker.")
    st.markdown("---")
    
    st.markdown("### 💊 Active Medication List")
    meds = list_medications_db()
    if meds:
        for med in meds:
            st.html(f"""
            <div class="card med-card">
                <strong>{med['name'].capitalize()}</strong> ({med['dose']})<br/>
                <span style="font-size:0.85rem; color:#94a3b8;">
                    🔄 {med['frequency']}<br/>
                    📅 Start: {med['start_date']}<br/>
                    {f"📅 End: {med['end_date']}<br/>" if med['end_date'] else ""}
                    {f"📝 {med['notes']}" if med['notes'] else ""}
                </span>
            </div>
            """)
            
            # Remove button
            if st.button(f"🗑️ Remove {med['name'].capitalize()}", key=f"del_{med['name']}"):
                remove_medication_db(med['name'])
                st.session_state.status_message = ("success", f"Successfully removed {med['name'].capitalize()} from database.")
                st.rerun()
    else:
        st.info("No medications added yet. Use the chat or form to add your medications.")

    st.markdown("---")
    st.markdown("### ⏰ Daily Reminders")
    reminders = list_reminders_db()
    if reminders:
        for rem in reminders:
            st.html(f"""
            <div class="card reminder-card">
                <strong>{rem['medication_name'].capitalize()}</strong><br/>
                <span style="font-size:0.85rem; color:#94a3b8;">🕒 Scheduled for {rem['reminder_time']}</span>
            </div>
            """)
    else:
        st.info("No reminders scheduled yet.")

# ----------------- MAIN INTERFACE -----------------
st.markdown('<h1 class="main-title">MedMate Concierge</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Secure Personal Medication Assistant & Drug Safety Guard</div>', unsafe_allow_html=True)

render_status()

# Tabs for features
tab_chat, tab_add, tab_interactions, tab_summary = st.tabs([
    "💬 Chat Concierge", 
    "➕ Add Medication", 
    "🔍 Drug Interaction Checker", 
    "📄 Prescription Summarizer"
])

# 1. Chat Concierge Tab
with tab_chat:
    st.markdown("### Chat with MedMate")
    st.markdown("Ask questions, add medications naturally, check interaction warnings, or schedule daily pill reminders.")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        role = msg["role"]
        content = msg["content"]
        with st.chat_message(role):
            st.markdown(content)
            
    # Chat Input
    if prompt := st.chat_input("Enter your request (e.g., 'Add Ibuprofen 400mg once daily starting today')"):
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("MedMate is thinking..."):
                response = run_agent(prompt)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# 2. Add Medication Tab
with tab_add:
    st.markdown("### Manual Medication Form")
    with st.form("medication_form"):
        name = st.text_input("Medication Name", placeholder="e.g., Lisinopril")
        dose = st.text_input("Dose / Strength", placeholder="e.g., 10mg")
        frequency = st.text_input("Frequency", placeholder="e.g., Once daily in the morning")
        start_date = st.date_input("Start Date")
        end_date_opt = st.checkbox("Specify End Date?")
        end_date = st.date_input("End Date") if end_date_opt else None
        notes = st.text_area("Additional Notes (Optional)", placeholder="Take with food, avoid grapefruit juice, etc.")
        
        # Reminder scheduling checkbox
        schedule_rem = st.checkbox("Schedule daily intake reminder?")
        rem_time = st.text_input("Reminder Time (HH:MM, 24-hr format)", value="08:00")
        
        submitted = st.form_submit_button("Save Medication")
        if submitted:
            if not name.strip() or not dose.strip() or not frequency.strip():
                st.session_state.status_message = ("error", "Please fill in all required fields (Name, Dose, and Frequency).")
                st.rerun()
            else:
                success = add_medication_db(
                    name=name,
                    dose=dose,
                    frequency=frequency,
                    start_date=str(start_date),
                    end_date=str(end_date) if end_date else None,
                    notes=notes
                )
                if success:
                    rem_msg = ""
                    if schedule_rem:
                        rem_success = add_reminder_db(name, rem_time)
                        if rem_success:
                            rem_msg = f" and reminder set at {rem_time}"
                        else:
                            rem_msg = " (failed to schedule reminder)"
                            
                    st.session_state.status_message = ("success", f"Successfully saved {name.capitalize()}{rem_msg} to database!")
                    st.rerun()
                else:
                    st.session_state.status_message = ("error", f"Failed to save {name.capitalize()} medication details.")
                    st.rerun()

# 3. Drug Interaction Checker Tab
with tab_interactions:
    st.markdown("### Search Drug Interactions")
    st.markdown("Check potential side effects or warnings between multiple medicines.")
    
    # Selection of current drugs or input manually
    available_drugs = [med['name'].capitalize() for med in meds]
    
    selected_drugs = st.multiselect("Select medications from your active list:", available_drugs)
    manual_drugs_input = st.text_input("Or enter medications manually (comma-separated):", placeholder="e.g., aspirin, ibuprofen")
    
    if st.button("Check Interactions", key="run_interaction_btn"):
        # Combine lists
        med_list = [d.strip().lower() for d in selected_drugs]
        if manual_drugs_input:
            med_list.extend([d.strip().lower() for d in manual_drugs_input.split(",") if d.strip()])
            
        # Deduplicate
        med_list = list(set(med_list))
        
        if len(med_list) < 2:
            st.error("Please select or enter at least two medications to perform interaction check.")
        else:
            with st.spinner("Checking RxNav interaction database..."):
                interaction_result = check_interactions(med_list)
                st.markdown(interaction_result)

# 4. Prescription Summarizer Tab
with tab_summary:
    st.markdown("### Simplify Prescription Text")
    st.markdown("Paste doctor's instructions or raw prescription labels to simplify instructions into clean language.")
    
    prescription_raw = st.text_area("Paste Prescription Instructions Here:", 
                                    placeholder="e.g., Metformin 500mg. Take 1 tablet by mouth twice daily with breakfast and dinner. Do not crush. Warn patient of GI side effects.", 
                                    height=150)
    
    if st.button("Generate Easy-to-Read Summary", key="run_summary_btn"):
        if not prescription_raw.strip():
            st.error("Please paste prescription text to generate a summary.")
        else:
            with st.spinner("Simplifying text..."):
                summary_output = summarize_prescription(prescription_raw)
                st.markdown(summary_output)

# Footer and Medical Disclaimer
st.markdown("""
<div class="medical-disclaimer">
    <strong>⚠️ Medical Disclaimer:</strong> MedMate is an AI assistant developed for educational and organizational purposes. 
    It cannot diagnose medical conditions, recommend drug dosages, or replace qualified medical professionals. 
    Always consult with your physician or a registered pharmacist before making decisions regarding your health or medications.
</div>
""", unsafe_allow_html=True)
