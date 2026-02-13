
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

# Custom CSS for Valentine's theme
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #fff0f5 0%, #ffe6e6 100%);
    }
    
    /* Titles */
    h1 {
        color: #d63384;
        font-family: 'Brush Script MT', cursive;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Captions */
    .stCaption {
        color: #a64d79;
        text-align: center;
        font-style: italic;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background-color: transparent;
    }
    
    /* User Message */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(255, 255, 255, 0.6);
        border-radius: 20px;
        padding: 10px;
        border: 1px solid #ffcccc;
    }
    
    /* AI Message */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: rgba(255, 240, 245, 0.8);
        border-radius: 20px;
        padding: 10px;
        border: 1px solid #ffb3d9;
    }
    
    /* Input Box */
    .stChatInput {
        border-radius: 20px !important;
        border-color: #ffb3d9 !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #fff0f5;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.5rem !important;
        }
        
        .stChatMessage {
            padding: 8px !important;
            font-size: 0.9rem !important;
            color: #333333 !important;
        }
        
        .stChatInput {
            font-size: 0.9rem !important;
        }
        
        /* Ensure sidebar doesn't take too much space on mobile */
        [data-testid="stSidebar"] {
            min-width: 250px !important;
        }
        
        /* Fix text color in chat messages */
        .stChatMessage p, .stChatMessage div {
            color: #333333 !important;
        }
    }
    
    /* Very small screens (phones in portrait) */
    @media (max-width: 480px) {
        h1 {
            font-size: 1.2rem !important;
        }
        
        .stChatMessage {
            padding: 6px !important;
            font-size: 0.85rem !important;
            color: #333333 !important;
        }
        
        /* Fix text color in chat messages */
        .stChatMessage p, .stChatMessage div {
            color: #333333 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("💖 Our Love Story 💖")
st.caption("Ask me anything about your conversations together!")

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
