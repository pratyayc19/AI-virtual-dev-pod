# ui/streamlit_app.py
# Streamlit UI — RFI Input + Live Agent Outputs — Person 1

import streamlit as st
import sys, os, time as t, io, threading, queue
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.project_lead import run_pipeline

st.set_page_config(
    page_title="AI Virtual Dev Pod",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI-Powered Virtual Development Pod")
st.markdown("*Upload an RFI document — watch each agent deliver its output live*")
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

# ── Session State ──────────────────────────────────────────────────
if "results"      not in st.session_state: st.session_state.results      = None
if "current_req"  not in st.session_state: st.session_state.current_req  = None
if "rerun_count"  not in st.session_state: st.session_state.rerun_count  = 0
if "rfi_text"     not in st.session_state: st.session_state.rfi_text     = None
if "rfi_name"     not in st.session_state: st.session_state.rfi_name     = None
if "running"      not in st.session_state: st.session_state.running      = False
if "show_critic"  not in st.session_state: st.session_state.show_critic  = False

# ── Extract text from RFI file ─────────────────────────────────────
def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    raw  = uploaded_file.read()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        return "".join([p.extract_text() or "" for p in reader.pages]).strip()
    elif name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(raw))
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()]).strip()
    return ""

# ── RFI Upload Section ─────────────────────────────────────────────
st.subheader("📄 Upload RFI Document")
col_upload, col_info = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload your RFI (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Request for Information document with project requirements"
    )
    if uploaded_file:
        if st.session_state.rfi_name != uploaded_file.name:
            with st.spinner("📖 Reading RFI document..."):
                extracted = extract_text(uploaded_file)
                if extracted:
                    st.session_state.rfi_text    = extracted
                    st.session_state.rfi_name    = uploaded_file.name
                    st.session_state.results     = None
                    st.session_state.rerun_count = 0
                    st.session_state.show_critic = False
                    for key in st.session_state.agent_status:
                        st.session_state.agent_status[key] = "⏳ Standby"
                else:
                    st.error("❌ Could not extract text. Please check the file.")

        if st.session_state.rfi_text:
            st.success(f"✅ **{uploaded_file.name}** — {len(st.session_state.rfi_text)} characters extracted")
            with st.expander("👁️ Preview RFI content"):
                st.text(st.session_state.rfi_text[:2000] + ("..." if len(st.session_state.rfi_text) > 2000 else ""))

with col_info:
    st.info("""
**What is an RFI?**
- 📋 Project background
- 🎯 Business objectives
- ⚙️ Functional requirements
- 🔧 Technical requirements
- ⏱️ Timeline & constraints
    """)

st.divider()

# ── Green Run Pipeline Button ──────────────────────────────────────
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #1a7a1a;
        border: none;
        color: white;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #228B22;
        border: none;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

if st.session_state.rfi_text and not st.session_state.running:
    run_clicked = st.button("🏃 Run Pipeline", type="primary", use_container_width=True)
else:
    run_clicked = False
    label = "⏳ Pipeline Running..." if st.session_state.running else "⬆️ Upload an RFI first"
    st.button(label, disabled=True, use_container_width=True)

# ── Live Pipeline Execution ────────────────────────────────────────
if run_clicked:
    st.session_state.running     = True
    st.session_state.results     = None
    st.session_state.rerun_count = 0
    st.session_state.show_critic = False
    st.session_state.current_req = st.session_state.rfi_text
    for key in st.session_state.agent_status:
        st.session_state.agent_status[key] = "⏳ Running..."

    st.subheader("🔄 Live Agent Outputs")
    st.caption("Each agent's output appears below as it completes")

    # Only 5 visible agents — critic is hidden
    agent_containers = {
        "brief":   {"label": "🧑‍💼 Project Lead Agent",   "lang": "markdown"},
        "stories": {"label": "📋 Business Analyst Agent", "lang": "markdown"},
        "design":  {"label": "🎨 Design Agent",           "lang": "markdown"},
        "code":    {"label": "💻 Developer Agent",        "lang": "python"},
        "tests":   {"label": "🧪 Testing Agent",          "lang": "markdown"},
    }

    # Create expanders upfront — all start as pending
    placeholders = {}
    for key, info in agent_containers.items():
        with st.expander(f"{info['label']} — ⏳ Waiting...", expanded=False):
            placeholders[key] = st.empty()
            placeholders[key].info("Waiting for agent to complete...")

    # Queue for live updates
    output_queue   = queue.Queue()
    pipeline_done  = [False]
    pipeline_error = [None]
    final_results  = [None]

    # Monkey-patch safe_output to push outputs to queue as they finish
    def run_with_live(rfi_text):
        import agents.project_lead as pl

        original_safe = pl.safe_output

        def patched_safe(input_text, output_text, agent_name, is_code=False):
            result, conf = original_safe(input_text, output_text, agent_name, is_code)
            key_map = {
                "Project Lead":    "brief",
                "BA Agent":        "stories",
                "Design Agent":    "design",
                "Developer Agent": "code",
                "Testing Agent":   "tests",
                "Critic Agent":    "review",
            }
            k = key_map.get(agent_name)
            if k:
                output_queue.put({"key": k, "text": result, "agent": agent_name})
            return result, conf

        pl.safe_output = patched_safe
        try:
            final_results[0] = pl.run_pipeline(rfi_text)
        except Exception as e:
            pipeline_error[0] = str(e)
        finally:
            pl.safe_output = original_safe
            pipeline_done[0] = True

    thread = threading.Thread(target=run_with_live, args=(st.session_state.rfi_text,))
    thread.start()

    # Poll queue and update UI live
    status_map = {
        "brief":   "🧑‍💼 Project Lead",
        "stories": "📋 BA Agent",
        "design":  "🎨 Design Agent",
        "code":    "💻 Developer",
        "tests":   "🧪 Tester",
        "review":  "🔁 Critic",
    }
    completed = set()

    while not pipeline_done[0] or not output_queue.empty():
        try:
            item = output_queue.get(timeout=1)
            key  = item["key"]
            text = item["text"]

            if key not in completed:
                completed.add(key)

                # Critic runs silently — no live display
                if key == "review":
                    st.session_state.agent_status["🔁 Critic"] = "✅ Done"
                    continue

                info = agent_containers[key]
                if info["lang"] == "python":
                    placeholders[key].code(text, language="python")
                else:
                    placeholders[key].markdown(text)

                sidebar_key = status_map.get(key)
                if sidebar_key and sidebar_key in st.session_state.agent_status:
                    st.session_state.agent_status[sidebar_key] = "✅ Done"

        except queue.Empty:
            t.sleep(0.5)
            continue

    thread.join()

    if pipeline_error[0]:
        st.error(f"❌ Error: {pipeline_error[0]}")
        if "rate_limit" in pipeline_error[0].lower():
            st.warning("⏳ Rate limit hit! Wait 1 minute and try again.")
        st.session_state.running = False
    else:
        st.session_state.results = final_results[0]
        st.session_state.running = False
        st.success("✅ All 6 agents completed!")
        st.rerun()

# ── Final Results ──────────────────────────────────────────────────
if st.session_state.results and not st.session_state.running:
    r = st.session_state.results
    st.divider()

    # Memory hit
    if r.get("memory_hit"):
        st.info("🧠 **Memory Hit!** Found a similar past RFI in ChromaDB!")

    # Re-run button — capped at 2 iterations
    rerun_count = st.session_state.rerun_count
    if "NEEDS_IMPROVEMENT" in r.get("review", "") and rerun_count < 2:
        st.warning(f"⚠️ **Critic flagged issues internally** — Re-run {rerun_count + 1}/2 available")
        if st.button("🔁 Re-run with Improvements", type="primary"):
            with st.spinner(f"🔁 Iteration {rerun_count + 1}: Developer improving code..."):
                new_results = run_pipeline(
                    st.session_state.current_req,
                    use_feedback=r.get("critic_feedback", "")
                )
                st.session_state.results     = new_results
                st.session_state.rerun_count = rerun_count + 1
                st.session_state.show_critic = False
                st.rerun()
    elif rerun_count >= 2:
        st.success("✅ **Max iterations reached (2/2). Final version locked in!**")
    elif "APPROVE" in r.get("review", ""):
        st.success("✅ **Code quality approved!**")

    # Final output tabs — 5 visible tabs, no critic
    st.subheader("📦 Pipeline Outputs")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Project Brief",
        "📝 User Stories",
        "🎨 Design",
        "💻 Code",
        "🧪 Tests",
    ])
    with tab1: st.markdown(r.get("brief", ""))
    with tab2: st.markdown(r.get("stories", ""))
    with tab3:
        design_text = r.get("design", "")
        if "```mermaid" in design_text:
            parts = design_text.split("```mermaid")
            st.markdown(parts[0])
            mermaid_raw = parts[1].split("```")[0].strip()
            st.subheader("📊 System Flow Diagram")
            st.markdown(f"```mermaid\n{mermaid_raw}\n```")
        else:
            st.markdown(design_text)
    with tab4: st.code(r.get("code", ""), language="python")
    with tab5: st.markdown(r.get("tests", ""))

    # Critic review — hidden, revealed only on button click
    st.divider()
    if not st.session_state.show_critic:
        if st.button("🔍 View Internal Quality Review"):
            st.session_state.show_critic = True
            st.rerun()
    else:
        st.subheader("🔁 Internal Quality Review")
        st.markdown(r.get("review", ""))
        if r.get("critic_feedback"):
            st.info(f"💬 **Feedback for Developer:** {r.get('critic_feedback')}")
        if st.button("🙈 Hide Review"):
            st.session_state.show_critic = False
            st.rerun()