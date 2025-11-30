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
    st.error("⚠️ GEMINI_API_KEY missing! Check your .env or Streamlit Secrets.")
    st.stop()

if not TAVILY_API_KEY:
    st.error("⚠️ TAVILY_API_KEY missing! Check your .env or Streamlit Secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

MODEL_ID = "gemini-2.0-flash"


def search_web(query):
    """
    Searches the web for accurate information using Tavily.
    Returns raw JSON context to be processed by the LLM.
    """
    try:

        response = tavily.search(query=query, search_depth="basic", max_results=5)
        return str(response)
    except Exception as e:
        return f"Search error: {str(e)}"


try:
    model = genai.GenerativeModel(MODEL_ID)
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

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

    with st.spinner("🕵️ Researcher Agent is finding study materials..."):
        search_context = search_web(user_input)

    prompt = f"""
    You are an expert AI Tutor. Your goal is to teach the user about: "{user_input}".
    
    I have performed a real-time web search for you. Here is the raw research data:
    {search_context}
    
    INSTRUCTIONS:
    1. Read the research data above.
    2. Explain the concept "{user_input}" clearly and concisely (approx 3 sentences).
    3. Generate ONE conceptual multiple-choice question to test the user's understanding.
    4. Provide the correct answer and a brief explanation in a spoiler tag or at the end.
    
    If the research data is empty, rely on your internal knowledge but mention that live data was unavailable.
    """

    with st.spinner("👨‍🏫 Tutor Agent is generating your lesson..."):
        try:
            chat = model.start_chat(history=st.session_state.chat_history)
            response = chat.send_message(prompt)

            st.chat_message("assistant").markdown(response.text)

            st.session_state.chat_history = chat.history

        except Exception as e:
            st.error(f"An error occurred: {e}")
