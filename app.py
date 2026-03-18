# =====================================================
# UMT POLICY CHATBOT - FRONTEND v3.1
# Runs on Streamlit (locally or Streamlit Cloud)
# Install: pip install streamlit requests
# Run: streamlit run app.py
# =====================================================

import streamlit as st
import requests
from datetime import datetime

# =====================================================
# CONFIGURATION
# =====================================================

# Paste your ngrok URL from Colab here
BACKEND_URL = "PASTE_YOUR_NGROK_URL_HERE"

# =====================================================
# PAGE SETUP
# =====================================================

st.set_page_config(
    page_title="UMT Policy Chatbot",
    page_icon="🎓",
    layout="centered"
)

# =====================================================
# STYLING
# =====================================================

st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 1rem 0;
        }
        .user-message {
            background-color: #e8f4fd;
            border-left: 4px solid #1f77b4;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .bot-message {
            background-color: #f0f2f6;
            border-left: 4px solid #2ca02c;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .source-tag {
            background-color: #e1ecf4;
            border-radius: 5px;
            padding: 0.2rem 0.6rem;
            font-size: 0.8rem;
            color: #0066cc;
            margin-right: 5px;
        }
        .relevance-tag {
            color: #888;
            font-size: 0.8rem;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
    <div class='main-header'>
        <h1>🎓 UMT Policy Chatbot</h1>
        <p style='color: gray;'>Ask me anything about UMT undergraduate policies</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "backend_url" not in st.session_state:
    st.session_state.backend_url = BACKEND_URL

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.header("⚙️ Settings")

    # Backend URL input
    backend_input = st.text_input(
        "Backend URL (ngrok)",
        value=st.session_state.backend_url,
        placeholder="https://xxxx.ngrok.io"
    )
    if backend_input:
        st.session_state.backend_url = backend_input

    # Check backend connection
    if st.button("🔍 Check Connection"):
        try:
            res = requests.get(
                f"{st.session_state.backend_url}/health",
                timeout=5
            )
            if res.status_code == 200:
                data = res.json()
                st.success("✅ Connected!")
                st.info(f"📚 {data.get('chunks', 0)} chunks loaded")
                st.info(f"🤖 {data.get('model', 'Unknown')}")
            else:
                st.error("❌ Backend returned error")
        except Exception as e:
            st.error(f"❌ Cannot connect: {str(e)}")

    st.divider()

    # Example questions
    st.subheader("💡 Example Questions")
    examples = [
        "What is the minimum attendance requirement?",
        "How do I freeze my semester?",
        "What happens if I fail a course?",
        "How do I apply for a scholarship?",
        "What are the hostel rules?",
        "Can I withdraw from a course?",
        "What is the grading policy?",
        "What is the fee refund policy?",
    ]

    for example in examples:
        if st.button(example, key=f"btn_{example}"):
            st.session_state.pending_question = example

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("UMT Policy Chatbot v3.1")
    st.caption("RAG + flan-t5-large (8-bit)")


# =====================================================
# CHAT DISPLAY
# =====================================================

for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.markdown(f"""
            <div class='user-message'>
                <b>🧑 You:</b><br>{msg['content']}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='bot-message'>
                <b>🤖 Assistant:</b><br>{msg['content']}
            </div>
        """, unsafe_allow_html=True)

        if 'sources' in msg and msg['sources']:
            st.markdown("📚 **Sources:**")
            for src in msg['sources']:
                st.markdown(f"""
                    <span class='source-tag'>{src['sub_category']}</span>
                    <span class='relevance-tag'>{src['similarity']:.1%} relevance</span>
                """, unsafe_allow_html=True)

        st.markdown("")


# =====================================================
# HELPER FUNCTION
# =====================================================

def ask_question(question):
    """Send question to Colab backend and return answer"""
    try:
        response = requests.post(
            f"{st.session_state.backend_url}/ask",
            json={'question': question},
            timeout=120
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                'answer': f"Backend error: {response.status_code}",
                'sources': []
            }

    except requests.exceptions.Timeout:
        return {
            'answer': "⚠️ Request timed out. Please try again.",
            'sources': []
        }
    except Exception as e:
        return {
            'answer': f"⚠️ Connection error: {str(e)}\n\nMake sure your Colab backend is running and the URL is correct.",
            'sources': []
        }


# =====================================================
# CHAT INPUT
# =====================================================

pending = st.session_state.get("pending_question", None)
user_input = st.chat_input("Ask about UMT policies...")

question_to_ask = pending if pending else user_input

if question_to_ask:
    if "pending_question" in st.session_state:
        del st.session_state.pending_question

    # Add user message to history
    st.session_state.messages.append({
        'role': 'user',
        'content': question_to_ask
    })

    # Call backend
    with st.spinner("🔍 Searching policies and generating answer..."):
        result = ask_question(question_to_ask)

    # Add assistant response to history
    st.session_state.messages.append({
        'role': 'assistant',
        'content': result.get('answer', 'No answer returned.'),
        'sources': result.get('sources', [])
    })

    st.rerun()


# =====================================================
# EMPTY STATE MESSAGE
# =====================================================

if not st.session_state.messages:
    st.markdown("""
        <div style='text-align: center; color: gray; padding: 3rem 0;'>
            <h3>👋 Welcome!</h3>
            <p>Ask me anything about UMT undergraduate policies.</p>
            <p>Use the example questions in the sidebar to get started.</p>
            <br>
            <p style='font-size: 0.85rem;'>
                Make sure your Colab backend is running before asking questions.
            </p>
        </div>
    """, unsafe_allow_html=True)
