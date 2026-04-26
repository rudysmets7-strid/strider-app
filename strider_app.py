import streamlit as st
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="STRIDER Architect", page_icon="🏗️", layout="wide")

# --- UI HEADER ---
st.title("🏗️ STRIDER Prompt Architect")
st.markdown("*Design, Audit, and Score your AI prompts for production.*")

# --- SECRETS & API SETUP ---
# It looks for the API key in Streamlit's secure secrets vault
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("🚨 API Key not found! Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

# --- LOAD KNOWLEDGE BASE ---
@st.cache_data
def load_system_prompt():
    with open("system_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()

system_instruction = load_system_prompt()

# Initialize the Gemini 1.5 Flash model (Fast, free, massive context)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# --- SIDEBAR UI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8297/8297053.png", width=100) # Placeholder icon, you can link your real one
    st.header("⚙️ App Settings")
    
    # Mode Selector
    st.markdown("### Select a Mode:")
    mode = st.radio(
        "Mode:",["🏗️ BUILD (Start from scratch)", 
         "🔍 AUDIT (Critique a prompt)", 
         "✍️ REWRITE (Improve a prompt)", 
         "📊 SCORE (Grade for production)", 
         "⚖️ COMPARE (A/B Test 2 prompts)"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages =[]
        st.rerun()

# --- CHAT HISTORY INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages =[]

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- USER INPUT ---
user_input = st.chat_input("Type your rough idea, or paste an existing prompt here...")

if user_input:
    # 1. Show user message in UI
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 2. Add to session history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 3. Format the final prompt to send to Gemini, enforcing the selected mode
    # We strip the emoji from the mode string for the system logic
    selected_mode_text = mode.split(" ", 1)[1] 
    engineered_prompt = f"MODE SELECTED: {selected_mode_text}\n\nUSER INPUT:\n{user_input}\n\nExecute the workflow for the selected mode."

    # 4. Generate AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # We use a chat session so the AI remembers context within the conversation
        chat = model.start_chat(history=[])
        
        with st.spinner("Analyzing via STRIDER Framework..."):
            response = chat.send_message(engineered_prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
    
    # 5. Save AI response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})