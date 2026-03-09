# Streamlit UI - Person 1
# ui/streamlit_app.py
# Streamlit Chat UI — Person 1 (Team Lead)
# ui/streamlit_app.py
# Streamlit UI — Full Pipeline — Person 1

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.project_lead import run_pipeline

st.set_page_config(
    page_title="AI Virtual Dev Pod",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI-Powered Virtual Development Pod")
st.markdown("*Simulate a full IT project team using AI agents*")
st.divider()

# Sidebar
with st.sidebar:
    st.header("📊 Pipeline Status")
    if "pipeline_status" not in st.session_state:
        st.session_state.pipeline_status = {
            "Project Lead": "⏳ Standby",
            "BA Agent":     "⏳ Standby",
            "Design Agent": "⏳ Standby",
            "Developer":    "⏳ Standby",
            "Tester":       "⏳ Standby",
            "Critic":       "⏳ Standby",
        }
    for agent, status in st.session_state.pipeline_status.items():
        st.markdown(f"**{agent}** — {status}")
    st.divider()
    st.markdown("**Tech Stack:**")
    st.markdown("🔗 CrewAI + LangChain")
    st.markdown("🧠 Groq LLaMA 3.1")
    st.markdown("🗄️ ChromaDB RAG")
    st.markdown("☁️ AWS Bedrock (Prod)")
    st.markdown("🛡️ Responsible AI Layer")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋 Hello! I'm your AI Project Lead. Give me a business requirement and I'll spin up the **full development team** — BA, Designer, Developer, Tester and Critic — to build it for you!"
    }]

if "results" not in st.session_state:
    st.session_state.results = None

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Show results tabs if available
if st.session_state.results:
    st.divider()
    st.subheader("📦 Pipeline Outputs")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Project Brief",
        "📝 User Stories",
        "🎨 Design",
        "💻 Code",
        "🧪 Tests",
        "🔁 Review"
    ])
    with tab1: st.markdown(st.session_state.results.get("brief", ""))
    with tab2: st.markdown(st.session_state.results.get("stories", ""))
    with tab3: st.markdown(st.session_state.results.get("design", ""))
    with tab4: st.code(st.session_state.results.get("code", ""), language="python")
    with tab5: st.markdown(st.session_state.results.get("tests", ""))
    with tab6: st.markdown(st.session_state.results.get("review", ""))

# Chat input
if prompt := st.chat_input("Enter your business requirement..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🚀 All agents are working... This takes 2-3 minutes!"):
            try:
                # Update sidebar status
                agents_order = ["Project Lead", "BA Agent", "Design Agent", "Developer", "Tester", "Critic"]
                for a in agents_order:
                    st.session_state.pipeline_status[a] = "✅ Done"

                results = run_pipeline(prompt)
                st.session_state.results = results

                response = """✅ **Full Pipeline Complete!**

🧑‍💼 Project Lead → 📋 BA Agent → 🎨 Design → 💻 Developer → 🧪 Tester → 🔁 Critic

**All 6 agents have completed their work!**
👇 See the full output in the tabs below."""

                st.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()

            except Exception as e:
                err = f"❌ Error: {str(e)}"
                st.error(err)
                if "rate_limit" in str(e).lower():
                    st.warning("⏳ Groq rate limit hit! Wait 1 minute and try again.")
