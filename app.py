
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
import os

# Config must be first
st.set_page_config(page_title="Valentine's Chatbot", page_icon="❤️", layout="centered")

# Try to import rag_engine, but don't fail if dependencies aren't ready yet
try:
    from rag_engine import get_rag_chain
except ImportError:
    get_rag_chain = None

# Custom CSS for Premium Valentine's Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Pacifico&display=swap');

    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top left, #ff9a9e 0%, #fecfef 100%);
        font-family: 'Outfit', sans-serif;
    }
    
    /* Overlay to ensure readability */
    .main-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        z-index: -1;
    }

    /* Titles */
    h1 {
        color: #c9184a !important;
        font-family: 'Pacifico', cursive !important;
        text-align: center;
        font-size: 3.5rem !important;
        padding-top: 1rem !important;
        text-shadow: 2px 2px 10px rgba(255, 75, 110, 0.3);
    }
    
    /* Captions/Subtitle - FORCE VISIBILITY */
    .stCaption, .custom-subtitle {
        color: #800f2f !important;
        text-align: center;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        background: rgba(255, 255, 255, 0.4);
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 2rem !important;
        display: block;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    /* Chat Container */
    [data-testid="stChatMessageContainer"] {
        padding: 1rem;
    }

    /* Chat Messages - Glassmorphism */
    .stChatMessage {
        border-radius: 20px !important;
        margin-bottom: 15px !important;
        padding: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
    }

    /* User Message (Human) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background: rgba(255, 255, 255, 0.7) !important;
        border-left: 5px solid #ff4d6d !important;
    }
    
    /* AI Message (Robot) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(255, 182, 193, 0.4) !important;
        border-right: 5px solid #ff758f !important;
    }

    /* Force text color for messages */
    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        color: #4a0416 !important;
        font-weight: 400 !important;
    }

    /* Avatar Icons */
    [data-testid="stChatMessageAvatarIcon"] {
        background-color: #ff4d6d !important;
        color: white !important;
    }

    /* Input Box styling */
    .stChatInputContainer {
        border-radius: 30px !important;
        background: rgba(255, 255, 255, 0.8) !important;
        border: 2px solid #ff4d6d !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 192, 203, 0.3) !important;
        backdrop-filter: blur(15px);
    }

    /* Mobile Tweaks */
    @media (max-width: 768px) {
        h1 {
            font-size: 2.2rem !important;
        }
        .custom-subtitle {
            font-size: 0.95rem !important;
            width: 90%;
        }
        .stChatMessage {
            padding: 10px !important;
        }
    }
</style>
<div class="main-overlay"></div>
""", unsafe_allow_html=True)

st.title("💖 Our Love Story 💖")
st.markdown('<p class="custom-subtitle">✨ Ask me anything about your conversations together! ✨</p>', unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hi! ❤️ I've read all your messages together. Ask me anything about your conversations!")
    ]

# Sidebar
with st.sidebar:
    st.title("Settings ⚙️")
    st.markdown("---")
    if st.button("Reset Conversation 🔄"):
        st.session_state.chat_history = [
            AIMessage(content="Hi! ❤️ I've read all your messages together. Ask me anything about your conversations!")
        ]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Status:**")
    if os.path.exists("./faiss_index"):
        st.success("Memory Loaded! 🧠")
    else:
        st.error("Memory Not Found! ❌")
        st.info("Run `python ingest.py` first.")

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI", avatar="🤖"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human", avatar="🥰"):
            st.write(message.content)

# User input
user_query = st.chat_input("Type your message here...")

if user_query:
    # Add user message to history
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human", avatar="🥰"):
        st.write(user_query)

    # Generate response
    with st.chat_message("AI", avatar="🤖"):
        if not get_rag_chain:
            st.error("RAG Engine not loaded. Check dependencies.")
        elif not os.path.exists("./faiss_index"):
            st.error("Please run the ingestion script: `python ingest.py`")
        else:
            try:
                with st.spinner("Thinking... 🤔💭"):
                    if "rag_chain" not in st.session_state:
                        st.session_state.rag_chain = get_rag_chain()
                    
                    chain = st.session_state.rag_chain
                    
                    # Get response
                    # Pass recent history for context
                    response = chain.invoke({
                        "chat_history": st.session_state.chat_history[-6:-1], # Last 5 messages before current Query
                        "input": user_query
                    })
                    
                    answer = response["answer"]
                    st.write(answer)
                    
                    # Add AI response to history
                    st.session_state.chat_history.append(AIMessage(content=answer))
                    
            except Exception as e:
                st.error(f"Oops! Something went wrong: {e}")
