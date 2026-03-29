# =====================================================
# UMT POLICY CHATBOT - FRONTEND v4.0
# Runs on Streamlit Cloud
# Install: pip install streamlit requests
# Run locally: streamlit run app.py
# =====================================================

import streamlit as st
import requests

# =====================================================
# CONFIGURATION
# Update this URL every time you restart Colab
# =====================================================
BACKEND_URL = "https://euphuistical-mollie-nonhazardous.ngrok-free.dev"

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

# =====================================================
# SIDEBAR — Examples and Clear only, no URL input
# =====================================================
with st.sidebar:
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
        "What is the exam policy?",
        "How do I apply for a degree certificate?",
    ]

    for example in examples:
        if st.button(example, key=f"btn_{example}"):
            st.session_state.pending_question = example

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("UMT Policy Chatbot v4.0")
    st.caption("Powered by RAG + TinyLlama")

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

        st.markdown("📚 **Source:** UMT Handbook Undergraduate Studies 2025-2026")
st.markdown("")

# =====================================================
# HELPER FUNCTION
# =====================================================
def ask_question(question):
    """Send question to Colab backend and return answer"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={'question': question},
            timeout=120,
            headers={"ngrok-skip-browser-warning": "true"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                'answer': f"⚠️ Backend error: {response.status_code}. Please try again.",
                'sources': []
            }

    except requests.exceptions.Timeout:
        return {
            'answer': "⚠️ Request timed out. The model is taking too long. Please try again.",
            'sources': []
        }
    except Exception as e:
        return {
            'answer': "⚠️ The chatbot backend is currently offline. Please try again later.",
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

    st.session_state.messages.append({
        'role': 'user',
        'content': question_to_ask
    })

    with st.spinner("🔍 Searching policies and generating answer..."):
        result = ask_question(question_to_ask)

    st.session_state.messages.append({
        'role': 'assistant',
        'content': result.get('answer', 'No answer returned.'),
        'sources': result.get('sources', [])
    })

    st.rerun()

# =====================================================
# EMPTY STATE
# =====================================================
if not st.session_state.messages:
    st.markdown("""
        <div style='text-align: center; color: gray; padding: 3rem 0;'>
            <h3>👋 Welcome!</h3>
            <p>Ask me anything about UMT undergraduate policies.</p>
            <p>Use the example questions in the sidebar to get started.</p>
        </div>
    """, unsafe_allow_html=True)
