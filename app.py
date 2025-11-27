import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import os
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Configure Page
st.set_page_config(page_title="ExamPrep.AI", page_icon="🎓")

# 3. Setup Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ API Key not found! Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# --- HARDCODED MODEL SELECTION ---
# We selected this specific model from your available list.
# It is fast, smart, and free-tier friendly.
MODEL_ID = "models/gemini-2.0-flash"


# 4. Define the Tool
def search_web(query):
    """
    Searches the web for the latest information on a topic.
    """
    try:
        results = DDGS().text(query, max_results=3)
        if results:
            return "\n".join(
                [f"Title: {r['title']}\nSnippet: {r['body']}" for r in results]
            )
        return "No specific results found on the web."
    except Exception as e:
        return f"Search error: {str(e)}"


# 5. Initialize Model
tools_list = [search_web]

try:
    model = genai.GenerativeModel(MODEL_ID, tools=tools_list)
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# 6. Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- UI LAYOUT ---
st.title("🎓 ExamPrep Concierge")
st.caption(f"🤖 Powered by: `{MODEL_ID}`")

if st.sidebar.button("Clear Chat Memory"):
    st.session_state.chat_history = []
    st.rerun()

# 7. Main Logic
user_input = st.chat_input("Enter a topic (e.g., 'Operating Systems Deadlocks')...")

if user_input:
    st.chat_message("user").markdown(user_input)

    chat = model.start_chat(
        history=st.session_state.chat_history, enable_automatic_function_calling=True
    )

    prompt = f"""
    You are an advanced AI Study Assistant.
    
    STEP 1 (RESEARCHER): 
    The user is asking about: "{user_input}".
    Use the 'search_web' tool to find the absolute latest academic definitions and examples for this.
    
    STEP 2 (TUTOR):
    Based *only* on the search results:
    1. Explain the concept briefly (2-3 sentences).
    2. Ask the user ONE conceptual multiple-choice question to test their understanding.
    """

    with st.spinner("Researching definitions and preparing a quiz..."):
        try:
            response = chat.send_message(prompt)
            st.chat_message("assistant").markdown(response.text)
            st.session_state.chat_history = chat.history

        except Exception as e:
            st.error(f"An error occurred: {e}")
            if "429" in str(e):
                st.warning("⚠️ High traffic. Please wait 1 minute and try again.")
