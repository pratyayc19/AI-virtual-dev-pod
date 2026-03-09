# ui/streamlit_app.py
# Streamlit UI — All 4 Innovations — Person 1

import streamlit as st
import sys, os, time as t
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

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📊 Pipeline Status")
    if "agent_status" not in st.session_state:
        st.session_state.agent_status = {
            "🧑‍💼 Project Lead": "⏳ Standby",
            "📋 BA Agent":       "⏳ Standby",
            "🎨 Design Agent":   "⏳ Standby",
            "💻 Developer":      "⏳ Standby",
            "🧪 Tester":         "⏳ Standby",
            "🔁 Critic":         "⏳ Standby",
        }
    for agent, status in st.session_state.agent_status.items():
        st.markdown(f"**{agent}** — {status}")
    st.divider()
    st.markdown("**🛡️ Responsible AI**")
    st.markdown("✅ Input safety check")
    st.markdown("✅ Output guardrails")
    st.markdown("✅ PII redaction")
    st.divider()
    st.markdown("**Tech Stack:**")
    st.markdown("🔗 CrewAI + LangChain")
    st.markdown("🧠 Groq LLaMA 3.3")
    st.markdown("🗄️ ChromaDB RAG")
    st.markdown("☁️ AWS Bedrock (Prod)")

# ── Session State Init ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋 Hello! I'm your AI Project Lead. Give me a business requirement and I'll spin up the **full development team** to build it!\n\n**6 agents will run:** Project Lead → BA → Designer → Developer → Tester → Critic"
    }]
if "results"      not in st.session_state: st.session_state.results      = None
if "current_req"  not in st.session_state: st.session_state.current_req  = None
if "rerun_count"  not in st.session_state: st.session_state.rerun_count  = 0

# ── Chat History ───────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Results Display ────────────────────────────────────────────────
if st.session_state.results:
    r = st.session_state.results
    st.divider()

    # Memory notification
    if r.get("memory_hit"):
        st.info("🧠 **Memory Hit!** Found a similar past requirement in ChromaDB!")

    # Confidence Score Dashboard
    st.subheader("🎯 Agent Confidence Scores")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🧑‍💼 Lead",   f"{r.get('conf_lead', 0)}%")
    col2.metric("📋 BA",       f"{r.get('conf_ba', 0)}%")
    col3.metric("🎨 Design",   f"{r.get('conf_design', 0)}%")
    col4.metric("💻 Dev",      f"{r.get('conf_dev', 0)}%")
    col5.metric("🧪 Tester",   f"{r.get('conf_test', 0)}%")
    col6.metric("🔁 Critic",   f"{r.get('conf_critic', 0)}%")

    # Average confidence
    scores = [r.get(k, 0) for k in ['conf_lead','conf_ba','conf_design','conf_dev','conf_test','conf_critic']]
    valid  = [s for s in scores if s > 0]
    avg    = int(sum(valid) / len(valid)) if valid else 0
    st.markdown(f"**Overall Pipeline Confidence: {avg}%**")

    st.divider()

    # Re-run with improvements — capped at 2
    rerun_count = st.session_state.rerun_count
    if "NEEDS_IMPROVEMENT" in r.get("review", "") and rerun_count < 2:
        st.warning(f"⚠️ **Critic says NEEDS IMPROVEMENT** — Re-run {rerun_count + 1}/2 available")
        if st.button("🔁 Re-run with Critic Feedback", type="primary"):
            with st.spinner(f"🔁 Iteration {rerun_count + 1}: Improving code with critic feedback..."):
                feedback = r.get("critic_feedback", "")
                new_results = run_pipeline(
                    st.session_state.current_req,
                    use_feedback=feedback
                )
                st.session_state.results      = new_results
                st.session_state.rerun_count  = rerun_count + 1
                st.success(f"✅ Iteration {rerun_count + 1} complete!")
                st.rerun()

    elif rerun_count >= 2:
        st.success("✅ **Max iterations reached (2/2).** Final version locked in!")

    elif "APPROVE" in r.get("review", ""):
        st.success("✅ **Critic APPROVED the code!** No re-run needed.")

    # Output Tabs
    st.subheader("📦 Pipeline Outputs")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Project Brief",
        "📝 User Stories",
        "🎨 Design",
        "💻 Code",
        "🧪 Tests",
        "🔁 Review"
    ])
    with tab1: st.markdown(r.get("brief", ""))
    with tab2: st.markdown(r.get("stories", ""))
    with tab3: st.markdown(r.get("design", ""))
    with tab4: st.code(r.get("code", ""), language="python")
    with tab5: st.markdown(r.get("tests", ""))
    with tab6:
        st.markdown(r.get("review", ""))
        if r.get("critic_feedback"):
            st.info(f"💬 **Critic Feedback:** {r.get('critic_feedback')}")

# ── Chat Input ─────────────────────────────────────────────────────
if prompt := st.chat_input("Enter your business requirement..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.current_req = prompt
    st.session_state.rerun_count = 0  # Reset counter for new requirement
    for key in st.session_state.agent_status:
        st.session_state.agent_status[key] = "⏳ Running..."

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        # Live Progress Bar
        progress    = st.progress(0, text="🚀 Starting pipeline...")
        status_text = st.empty()

        steps = [
            (10,  "🧑‍💼 Project Lead analyzing requirements..."),
            (25,  "📋 BA Agent writing user stories..."),
            (40,  "🎨 Design Agent creating architecture..."),
            (58,  "💻 Developer Agent generating code..."),
            (75,  "🧪 Testing Agent running test cases..."),
            (88,  "🔁 Critic Agent reviewing quality..."),
            (95,  "🛡️ Running Responsible AI checks..."),
            (100, "✅ Pipeline complete!"),
        ]

        import threading
        pipeline_done   = [False]
        pipeline_result = [None]
        pipeline_error  = [None]

        def run_bg():
            try:
                pipeline_result[0] = run_pipeline(prompt)
            except Exception as e:
                pipeline_error[0] = str(e)
            finally:
                pipeline_done[0] = True

        thread = threading.Thread(target=run_bg)
        thread.start()

        step_idx = 0
        while not pipeline_done[0]:
            if step_idx < len(steps) - 2:
                pct, msg = steps[step_idx]
                progress.progress(pct, text=msg)
                status_text.markdown(f"*{msg}*")
                step_idx += 1
            t.sleep(8)

        thread.join()
        progress.progress(100, text="✅ Pipeline complete!")
        status_text.empty()

        if pipeline_error[0]:
            st.error(f"❌ Error: {pipeline_error[0]}")
            if "rate_limit" in pipeline_error[0].lower():
                st.warning("⏳ Rate limit hit! Wait 1 minute and try again.")
        else:
            results = pipeline_result[0]
            st.session_state.results = results
            for key in st.session_state.agent_status:
                st.session_state.agent_status[key] = "✅ Done"

            scores  = [results.get(k, 0) for k in ['conf_lead','conf_ba','conf_design','conf_dev','conf_test','conf_critic']]
            valid   = [s for s in scores if s > 0]
            avg     = int(sum(valid) / len(valid)) if valid else 0
            mem_msg = "\n\n🧠 **Memory:** Found a similar past requirement!" if results.get("memory_hit") else ""

            response = f"""✅ **Full Pipeline Complete!**

🧑‍💼 → 📋 → 🎨 → 💻 → 🧪 → 🔁 All 6 agents done!

**Overall Confidence: {avg}%**{mem_msg}

👇 See full outputs in the tabs below."""

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()