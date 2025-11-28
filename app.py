import streamlit as st
import google.generativeai as genai
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ExamPrep.AI", page_icon="🎓")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GEMINI_API_KEY:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except:
        pass

if not TAVILY_API_KEY:
    try:
        TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
    except:
        pass

if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI_API_KEY missing! Add it to .env or Streamlit Secrets.")
    st.stop()

if not TAVILY_API_KEY:
    st.error("⚠️ TAVILY_API_KEY missing! Add it to .env or Streamlit Secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)


MODEL_ID = "gemini-2.0-flash"


def search_web(query):
    """
    Searches the web for accurate information using Tavily (AI-Optimized Search).
    """
    try:
        # qna_search gives a direct answer optimized for agents
        response = tavily.qna_search(query=query)
        return response
    except Exception as e:
        return f"Search error: {str(e)}"


tools_list = [search_web]
model = genai.GenerativeModel(MODEL_ID, tools=tools_list)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🎓 ExamPrep Concierge")
st.caption("🤖 Powered by Gemini 2.0 Flash & Tavily Search")

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
