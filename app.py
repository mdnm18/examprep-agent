import streamlit as st
import google.generativeai as genai
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ExamPrep.AI", page_icon="🎓")


def get_key(name):
    try:
        val = st.secrets.get(name)
    except:
        val = None

    if not val:
        val = os.getenv(name)

    if val:
        return val.strip()
    return None


GEMINI_API_KEY = get_key("GEMINI_API_KEY")
TAVILY_API_KEY = get_key("TAVILY_API_KEY")

if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI_API_KEY missing! Check your Streamlit Secrets.")
    st.stop()

if not TAVILY_API_KEY:
    st.error("⚠️ TAVILY_API_KEY missing! Check your Streamlit Secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

MODEL_ID = "gemini-2.0-flash"


def search_web(query):
    """
    Searches the web using Tavily. Includes Error Logging.
    """
    try:
        response = tavily.qna_search(query=query)
        st.write("🔍 RAW TAVILY OUTPUT:", response)
        return response
    except Exception as e:
        error_msg = f"Search Tool Failed: {str(e)}"
        st.error(error_msg)
        return error_msg


tools_list = [search_web]
model = genai.GenerativeModel(MODEL_ID, tools=tools_list)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🎓 ExamPrep Concierge")
st.caption(f"🤖 Powered by {MODEL_ID} & Tavily Search")

if st.sidebar.button("Clear Chat Memory"):
    st.session_state.chat_history = []
    st.rerun()

user_input = st.chat_input("Enter a topic (e.g., 'React Hooks')...")

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
