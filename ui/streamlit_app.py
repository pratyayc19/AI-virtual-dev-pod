# Streamlit UI - Person 1
# ui/streamlit_app.py
# Streamlit Chat UI — Person 1 (Team Lead)

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.project_lead import run_pipeline

# Page config
st.set_page_config(
    page_title="AI Virtual Dev Pod",
    page_icon="🤖",
    layout="wide"
)

# Header
st.title("🤖 AI-Powered Virtual Development Pod")
st.markdown("*Simulate a full IT project team using AI agents*")
st.divider()

# Sidebar
with st.sidebar:
    st.header("📊 Pipeline Status")
    st.markdown("**Agents:**")
    st.markdown("🧑‍💼 Project Lead — Active")
    st.markdown("📋 BA Agent — Standby")
    st.markdown("🎨 Design Agent — Standby")
    st.markdown("💻 Developer Agent — Standby")
    st.markdown("🧪 Testing Agent — Standby")
    st.markdown("🔁 Critic Agent — Standby")
    st.divider()
    st.markdown("**Tech Stack:**")
    st.markdown("🔗 CrewAI + LangChain")
    st.markdown("🧠 Groq LLaMA 3.1")
    st.markdown("🗄️ ChromaDB (RAG)")
    st.markdown("☁️ AWS Bedrock (Prod)")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I'm your AI Project Lead. Give me a business requirement and I'll spin up the full development team to build it for you!"
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Enter your business requirement here..."):
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run pipeline
    with st.chat_message("assistant"):
        with st.spinner("🚀 Virtual Dev Pod is running... Agents are working!"):
            try:
                result = run_pipeline(prompt)
                response = f"""
✅ **Project Brief Generated!**

{result}

---
*🔄 Next: BA Agent will convert this into User Stories...*
                """
                st.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)

