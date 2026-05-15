import streamlit as st
from kavach_backend.agents.agent_manager import AgentManager
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Kavach AI", page_icon="🛡️", layout="wide")

st.title("🛡️ Kavach AI: Cyber-Safety Ecosystem")
st.markdown("Training your Reflexive Defenses against modern AI-enhanced fraud.")

# --- Sidebar & Setup ---
with st.sidebar:
    st.header("Simulation Control")
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_api_key_here":
        st.error("⚠️ GROQ_API_KEY not found or invalid in .env file.")
        st.info("Please add your Groq API key to the .env file in this directory. Get one free at https://console.groq.com")
        st.stop()
        
    modules = [
        "UPI Scams (The 'Receive' Request Trick)", 
        "Deepfake Voice Clones (Distress Calls)", 
        "Digital Arrest Scams (Fake Law Enforcement)", 
        "Targeted Phishing (Urgent Service Alert)"
    ]
    
    selected_module = st.selectbox("Select Training Module", modules)
    
    if st.button("Start/Reset Simulation"):
        st.session_state.messages = []
        
        with st.spinner("Initializing Agents..."):
            st.session_state.infiltrator = AgentManager("Infiltrator")
            st.session_state.forensic = AgentManager("Forensic")
            st.session_state.mentor = AgentManager("Mentor")
            
            # Start the flow
            intro_prompt = f"Introduce the {selected_module} cyber-safety module to the user. Keep it brief."
            mentor_intro = st.session_state.mentor.send_message(intro_prompt)
            st.session_state.messages.append({"role": "Mentor", "content": mentor_intro})
            
            attack_prompt = f"Start the {selected_module} attack on the user now. Just send your first attack message."
            infiltrator_attack = st.session_state.infiltrator.send_message(attack_prompt)
            st.session_state.messages.append({"role": "Infiltrator", "content": infiltrator_attack})

# --- Main Chat Interface ---

# Avatar dictionary
avatars = {
    "Infiltrator": "🦹",
    "Forensic": "🕵️",
    "Mentor": "🛡️",
    "User": "👤"
}

if "messages" not in st.session_state:
    st.info("👈 Please select a module and click 'Start Simulation' from the sidebar to begin.")
else:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=avatars.get(msg["role"], "🤖")):
            st.markdown(f"**{msg['role']}**\n\n{msg['content']}")
            
    # Input from User
    if user_input := st.chat_input("Type your response here..."):
        # Add user message
        st.session_state.messages.append({"role": "User", "content": user_input})
        with st.chat_message("User", avatar=avatars["User"]):
            st.markdown(f"**User**\n\n{user_input}")
            
        # Get last Infiltrator message
        last_infiltrator = ""
        for m in reversed(st.session_state.messages[:-1]):
            if m["role"] == "Infiltrator":
                last_infiltrator = m["content"]
                break
                
        # 1. Forensic Agent analyzes
        with st.spinner("Forensics analyzing..."):
            forensic_prompt = f"Analyze the following interaction for red flags.\nInfiltrator sent: '{last_infiltrator}'\nUser replied: '{user_input}'"
            forensic_response = st.session_state.forensic.send_message(forensic_prompt)
            st.session_state.messages.append({"role": "Forensic", "content": forensic_response})
            with st.chat_message("Forensic", avatar=avatars["Forensic"]):
                st.markdown(f"**Forensic**\n\n{forensic_response}")
                
        # 2. Defense Mentor gives feedback
        with st.spinner("Mentor evaluating..."):
            mentor_prompt = f"The user replied: '{user_input}' to the threat. The forensic agent said: '{forensic_response}'. Provide brief guidance and update their Cyber-Safety Health Score."
            mentor_response = st.session_state.mentor.send_message(mentor_prompt)
            st.session_state.messages.append({"role": "Mentor", "content": mentor_response})
            with st.chat_message("Mentor", avatar=avatars["Mentor"]):
                st.markdown(f"**Mentor**\n\n{mentor_response}")
                
        # 3. Infiltrator continues the attack
        with st.spinner("Adversary reacting..."):
            infiltrator_prompt = f"The user responded with: '{user_input}'. Continue your attack based on your persona."
            infiltrator_response = st.session_state.infiltrator.send_message(infiltrator_prompt)
            st.session_state.messages.append({"role": "Infiltrator", "content": infiltrator_response})
            with st.chat_message("Infiltrator", avatar=avatars["Infiltrator"]):
                st.markdown(f"**Infiltrator**\n\n{infiltrator_response}")

