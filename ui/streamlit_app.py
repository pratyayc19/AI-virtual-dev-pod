# ui/streamlit_app.py
# TetraGen — AI Operations Center — Person 1

import streamlit as st
import sys, os, time as t, io, threading, queue, re
import streamlit.components.v1 as components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.project_lead import run_pipeline

st.set_page_config(
    page_title="TetraGen — AI Dev Pod",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&family=Orbitron:wght@600;700;900&display=swap" rel="stylesheet">
<style>
:root {
    --bg:        #070b14;
    --bg2:       #0b1120;
    --bg3:       #0f1729;
    --panel:     #111827;
    --panel2:    #1a2235;
    --border:    #1e2d45;
    --border2:   #253552;
    --blue:      #00d4ff;
    --blue2:     #0ea5e9;
    --blue3:     #38bdf8;
    --purple:    #8b5cf6;
    --purple2:   #a78bfa;
    --green:     #10b981;
    --green2:    #34d399;
    --neon:      #00ff6a;
    --amber:     #f59e0b;
    --amber2:    #fbbf24;
    --red:       #ef4444;
    --pink:      #ec4899;
    --teal:      #14b8a6;
    --text:      #e2e8f0;
    --text2:     #94a3b8;
    --text3:     #475569;
    --white:     #f8fafc;
    --glow-b:    0 0 20px rgba(0,212,255,0.25);
    --glow-p:    0 0 20px rgba(139,92,246,0.25);
    --glow-g:    0 0 20px rgba(16,185,129,0.25);
}

* { box-sizing: border-box; }

.stApp {
    background: var(--bg) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Subtle dot grid */
.stApp::after {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(circle, rgba(0,212,255,0.05) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none; z-index: 0;
}

/* ── Sidebar ─────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* ── Layout ──────────────────────────────── */
.block-container { padding: 2.5rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Typography ──────────────────────────── */
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--white) !important;
    letter-spacing: -0.02em !important;
}
p, li, label, span, div {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text) !important;
}
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1rem 0 !important; }

/* ── Buttons ─────────────────────────────── */
.stButton > button {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.02em !important;
    border-radius: 6px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9, #8b5cf6) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(14,165,233,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(14,165,233,0.5) !important;
}
.stButton > button:not([kind="primary"]):not([disabled]) {
    background: var(--panel2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
}
.stButton > button:not([kind="primary"]):not([disabled]):hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
    box-shadow: var(--glow-b) !important;
}
.stButton > button[disabled] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text3) !important;
    opacity: 0.5 !important;
}

/* ── File uploader ───────────────────────── */
[data-testid="stFileUploaderDropzone"] {
    background: var(--panel) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 10px !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--blue) !important;
    background: rgba(0,212,255,0.03) !important;
    box-shadow: var(--glow-b) !important;
}

/* ── Expanders — use Arial so arrow renders correctly ── */
[data-testid="stExpander"] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stExpander"]:hover { border-color: var(--border2) !important; }
[data-testid="stExpander"] summary svg {
    display: none !important;
}
[data-testid="stExpander"] summary p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}

/* ── Tabs ────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 2px !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    color: var(--text2) !important;
    border: none !important;
    background: transparent !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: var(--panel2) !important;
    color: var(--white) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important;
}
[data-testid="stTabs"] [role="tab"]:hover { color: var(--white) !important; }

/* ── Code blocks ─────────────────────────── */
.stCode, pre, code {
    font-family: 'JetBrains Mono', monospace !important;
    background: var(--panel2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}

/* ── Markdown ────────────────────────────── */
[data-testid="stMarkdownContainer"] p   { font-size: 14px !important; line-height: 1.7 !important; color: var(--text) !important; }
[data-testid="stMarkdownContainer"] li  { font-size: 14px !important; line-height: 1.7 !important; color: var(--text) !important; }
[data-testid="stMarkdownContainer"] strong { color: var(--white) !important; }
[data-testid="stMarkdownContainer"] h1  { color: var(--white) !important; font-size: 20px !important; }
[data-testid="stMarkdownContainer"] h2  { color: var(--blue3) !important; font-size: 16px !important; }
[data-testid="stMarkdownContainer"] h3  { color: var(--purple2) !important; font-size: 14px !important; }
[data-testid="stMarkdownContainer"] code { color: var(--amber2) !important; background: var(--panel2) !important; padding: 1px 6px !important; border-radius: 4px !important; }

/* ── Alerts ──────────────────────────────── */
[data-testid="stAlert"] { border-radius: 8px !important; font-family: 'Space Grotesk', sans-serif !important; font-size: 13px !important; }

/* ── Scrollbar ───────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--blue2); }
</style>
""")

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
defaults = {
    "results": None, "current_req": None, "rerun_count": 0,
    "rfi_text": None, "rfi_name": None, "running": False,
    "show_critic": False,
    "agent_progress": {
        "Project Lead": "idle", "BA Agent": "idle", "Design Agent": "idle",
        "Developer": "idle", "Tester": "idle", "Critic": "idle"
    }
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
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


def render_flow_diagram(flow_text: str):
    steps = []
    for line in flow_text.splitlines():
        line = line.strip()
        if line.startswith("STEP:"):
            parts = line.replace("STEP:", "").split("|")
            label = parts[0].strip()
            stype = parts[1].replace("type:", "").strip() if len(parts) > 1 else "process"
            steps.append({"label": label, "type": stype})
    if not steps:
        return

    type_cfg = {
        "input":    {"bg": "#0c1f2e", "border": "#00d4ff", "color": "#00d4ff", "icon": "&#9654;",  "tag": "INPUT"},
        "process":  {"bg": "#0d1f14", "border": "#10b981", "color": "#10b981", "icon": "&#11044;", "tag": "PROCESS"},
        "decision": {"bg": "#1f1508", "border": "#f59e0b", "color": "#f59e0b", "icon": "&#9670;",  "tag": "DECISION"},
        "success":  {"bg": "#130d1f", "border": "#8b5cf6", "color": "#8b5cf6", "icon": "&#10003;", "tag": "SUCCESS"},
    }
    connector = (
        '<div style="display:flex;flex-direction:column;align-items:center;margin:0;">'
        '<div style="width:1px;height:12px;background:#1e2d45;"></div>'
        '<div style="color:#475569;font-size:10px;line-height:1;">&#9660;</div>'
        '<div style="width:1px;height:4px;background:#1e2d45;"></div>'
        '</div>'
    )
    boxes = ""
    for i, step in enumerate(steps):
        cfg = type_cfg.get(step["type"], type_cfg["process"])
        boxes += (
            '<div style="display:flex;flex-direction:column;align-items:center;">'
            '<div style="background:' + cfg['bg'] + ';border:1px solid ' + cfg['border'] + ';'
            'border-left:3px solid ' + cfg['border'] + ';color:' + cfg['color'] + ';'
            'font-family:Space Grotesk,sans-serif;font-size:13px;font-weight:500;'
            'padding:12px 18px;width:100%;display:flex;align-items:center;gap:10px;'
            'border-radius:6px;box-shadow:0 0 10px ' + cfg['border'] + '18;">'
            '<span>' + cfg['icon'] + '</span>'
            '<span>' + step['label'] + '</span>'
            '<span style="margin-left:auto;font-size:9px;opacity:0.45;'
            'font-family:JetBrains Mono,monospace;letter-spacing:0.1em;">'
            + cfg['tag'] + '</span></div>'
            + ('' if i == len(steps) - 1 else connector)
            + '</div>'
        )
    html = (
        '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500&family=JetBrains+Mono&display=swap" rel="stylesheet">'
        '<div style="background:#070b14;border:1px solid #1e2d45;border-radius:10px;padding:24px 28px;">'
        '<div style="font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:0.2em;'
        'color:#475569;text-transform:uppercase;margin-bottom:16px;">// SYSTEM EXECUTION FLOW</div>'
        + boxes + '</div>'
    )
    st.components.v1.html(html, height=len(steps) * 68 + 100, scrolling=False)


def section_label(num: str, title: str):
    st.markdown(
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:13px;font-weight:600;'
        f'color:#475569;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 10px 0;">'
        f'{num} &nbsp; {title}</div>',
        unsafe_allow_html=True
    )


def status_box(text: str, color: str, icon: str = ""):
    st.markdown(
        f'<div style="background:{color}12;border:1px solid {color};border-left:3px solid {color};'
        f'border-radius:8px;padding:10px 16px;margin-bottom:10px;'
        f'display:flex;align-items:center;gap:10px;">'
        f'{"<span>" + icon + "</span>" if icon else ""}'
        f'<span style="font-family:Space Grotesk,sans-serif;font-size:13px;'
        f'font-weight:500;color:{color};">{text}</span></div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0b1120,#111827);
        border-bottom:1px solid #1e2d45;padding:20px 16px 16px 16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <div style="width:32px;height:32px;
                background:linear-gradient(135deg,#0ea5e9,#8b5cf6);
                border-radius:8px;display:flex;align-items:center;justify-content:center;
                font-size:16px;font-weight:900;color:white;font-family:Space Grotesk,sans-serif;">T</div>
            <div>
                <div style="font-family:Space Grotesk,sans-serif;font-weight:700;
                    font-size:15px;color:#f8fafc;">TetraGen</div>
                <div style="font-family:JetBrains Mono,monospace;font-size:9px;
                    color:#475569;letter-spacing:0.1em;">AI DEV POD v2.0</div>
            </div>
            <div style="margin-left:auto;width:8px;height:8px;background:#10b981;
                border-radius:50%;box-shadow:0 0 8px #10b981;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Agent Pipeline label
    st.markdown("""
    <div style="padding:0 8px;margin-bottom:10px;">
        <span style="font-family:Space Grotesk,sans-serif;font-size:11px;font-weight:600;
            color:#475569;text-transform:uppercase;letter-spacing:0.12em;">
            Agent Pipeline</span>
    </div>
    """, unsafe_allow_html=True)

    agent_cfg = [
        {"key": "Project Lead",  "icon": "&#128203;", "role": "Orchestrator",    "color": "#00d4ff"},
        {"key": "BA Agent",      "icon": "&#128221;", "role": "Requirements",    "color": "#8b5cf6"},
        {"key": "Design Agent",  "icon": "&#127775;", "role": "Architecture",    "color": "#14b8a6"},
        {"key": "Developer",     "icon": "&#128187;", "role": "Code Generation", "color": "#f59e0b"},
        {"key": "Tester",        "icon": "&#128269;", "role": "Quality Check",   "color": "#10b981"},
        {"key": "Critic",        "icon": "&#128064;", "role": "Code Review",     "color": "#ec4899"},
    ]

    ap = st.session_state.agent_progress
    for i, ag in enumerate(agent_cfg):
        status = ap.get(ag["key"], "idle")
        bg     = {"idle": "#0f1729", "running": "#111827", "done": "#0d1f14"}.get(status, "#0f1729")
        bc     = {"idle": "#1e2d45", "running": ag["color"], "done": "#10b981"}.get(status, "#1e2d45")
        sc     = {"idle": "#475569", "running": ag["color"], "done": "#10b981"}.get(status, "#475569")
        sdot   = {"idle": "&#9675;", "running": "&#9679;", "done": "&#10003;"}.get(status, "&#9675;")
        slabel = {"idle": "IDLE", "running": "RUNNING", "done": "DONE"}.get(status, "IDLE")
        glow   = f"box-shadow:0 0 12px {ag['color']}40;" if status == "running" else ""

        st.markdown(f"""
        <div style="background:{bg};border:1px solid {bc};border-radius:8px;
            padding:10px 12px;margin-bottom:4px;transition:all 0.3s;{glow}">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:34px;height:34px;background:{ag['color']}18;
                    border:1px solid {ag['color']}40;border-radius:7px;
                    display:flex;align-items:center;justify-content:center;font-size:15px;">
                    {ag['icon']}</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-family:Space Grotesk,sans-serif;font-size:12px;
                        font-weight:600;color:#e2e8f0;">{ag['key']}</div>
                    <div style="font-family:JetBrains Mono,monospace;font-size:9px;
                        color:#475569;letter-spacing:0.05em;">{ag['role']}</div>
                </div>
                <div style="font-family:JetBrains Mono,monospace;font-size:9px;
                    color:{sc};letter-spacing:0.08em;text-align:right;white-space:nowrap;">
                    {sdot} {slabel}</div>
            </div>
        </div>
        {"" if i == len(agent_cfg) - 1 else '<div style="width:1px;height:5px;background:#1e2d45;margin:0 auto 4px auto;"></div>'}
        """, unsafe_allow_html=True)

    # Progress bar
    total = len(agent_cfg)
    done  = sum(1 for ag in agent_cfg if ap.get(ag["key"]) == "done")
    pct   = int(done / total * 100)
    bar_c = "#10b981" if pct == 100 else "#0ea5e9"
    st.markdown(f"""
    <div style="padding:0 4px;margin-top:14px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="font-family:Space Grotesk,sans-serif;font-size:11px;
                font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">
                Pipeline Progress</span>
            <span style="font-family:JetBrains Mono,monospace;font-size:11px;color:{bar_c};">
                {done}/{total}</span>
        </div>
        <div style="height:4px;background:#1e2d45;border-radius:4px;overflow:hidden;">
            <div style="height:100%;width:{pct}%;
                background:linear-gradient(90deg,#0ea5e9,#8b5cf6);
                border-radius:4px;transition:width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Responsible AI
    st.markdown("""
    <div style="margin-top:18px;padding-top:16px;border-top:1px solid #1e2d45;padding-left:4px;padding-right:4px;">
        <div style="font-family:Space Grotesk,sans-serif;font-size:11px;font-weight:600;
            color:#475569;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;">
            Responsible AI</div>
        <div style="display:flex;flex-direction:column;gap:6px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:6px;height:6px;background:#10b981;border-radius:50%;flex-shrink:0;"></div>
                <span style="font-family:Space Grotesk,sans-serif;font-size:12px;color:#94a3b8;">Input safety check</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:6px;height:6px;background:#10b981;border-radius:50%;flex-shrink:0;"></div>
                <span style="font-family:Space Grotesk,sans-serif;font-size:12px;color:#94a3b8;">Output guardrails</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:6px;height:6px;background:#10b981;border-radius:50%;flex-shrink:0;"></div>
                <span style="font-family:Space Grotesk,sans-serif;font-size:12px;color:#94a3b8;">PII redaction</span>
            </div>
        </div>
    </div>

    <div style="margin-top:18px;padding-top:16px;border-top:1px solid #1e2d45;padding-left:4px;padding-right:4px;">
        <div style="font-family:Space Grotesk,sans-serif;font-size:11px;font-weight:600;
            color:#475569;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;">
            Tech Stack</div>
        <div style="display:flex;flex-direction:column;gap:6px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:Space Grotesk,sans-serif;font-size:12px;color:#94a3b8;">Framework</span>
                <span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#00d4ff;">CrewAI</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:Space Grotesk,sans-serif;font-size:12px;color:#94a3b8;">LLM</span>
                <span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#8b5cf6;">Groq LLaMA</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:Space Grotesk,sans-serif;font-size:12px;color:#94a3b8;">Memory</span>
                <span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#14b8a6;">ChromaDB</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:Space Grotesk,sans-serif;font-size:12px;color:#94a3b8;">Database</span>
                <span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#f59e0b;">SQLite</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════

# ── Neon Header ─────────────────────────────────────────────────
st.markdown("""
<div style="border:1px solid #0a3d1a;border-left:4px solid #00ff6a;
    background:linear-gradient(135deg,#05140a 0%,#070b14 60%,#0b1120 100%);
    padding:20px 28px;margin-bottom:20px;position:relative;overflow:hidden;border-radius:8px;">
    <div style="position:absolute;top:-20px;right:-20px;width:180px;height:180px;border-radius:50%;
        background:radial-gradient(circle,rgba(0,255,106,0.05),transparent 70%);pointer-events:none;"></div>
    <div style="display:flex;align-items:center;justify-content:space-between;">
        <div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.3em;
                    color:#00ff6a;background:rgba(0,255,106,0.1);border:1px solid #00ff6a;
                    padding:2px 8px;border-radius:3px;">&#11044; SYSTEM ONLINE</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                    color:#4d8c66;letter-spacing:0.1em;">v2.0 // TETRAGEN MISSION CONTROL</div>
            </div>
            <div style="font-family:'Orbitron',monospace;font-size:26px;font-weight:900;
                letter-spacing:0.15em;text-transform:uppercase;
                background:linear-gradient(90deg,#00ff6a,#00ffe7,#c77dff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;margin-bottom:6px;">AI VIRTUAL DEV POD</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#4d8c66;">
                <span style="color:#00ff6a;">Upload RFI</span>
                <span style="color:#1a5c33;"> &#8594; </span>
                <span style="color:#00ffe7;">6 Agents Execute</span>
                <span style="color:#1a5c33;"> &#8594; </span>
                <span style="color:#c77dff;">Full SDLC Delivered</span>
            </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;">
            <div style="background:rgba(0,255,106,0.08);border:1px solid #00ff6a;
                border-radius:20px;padding:4px 12px;font-family:'JetBrains Mono',monospace;
                font-size:10px;color:#00ff6a;letter-spacing:0.1em;">&#9679; ONLINE</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                color:#4d8c66;letter-spacing:0.05em;">GROQ / CREWAI / CHROMADB</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── RFI Upload ───────────────────────────────────────────────────
section_label("01", "RFI Document Upload")

uploaded_file = st.file_uploader(
    "Upload RFI document",
    type=["pdf", "docx"],
    label_visibility="collapsed"
)

if uploaded_file:
    if st.session_state.rfi_name != uploaded_file.name:
        with st.spinner("Parsing document..."):
            extracted = extract_text(uploaded_file)
            if extracted:
                st.session_state.rfi_text    = extracted
                st.session_state.rfi_name    = uploaded_file.name
                st.session_state.results     = None
                st.session_state.rerun_count = 0
                st.session_state.show_critic = False
                for k in st.session_state.agent_progress:
                    st.session_state.agent_progress[k] = "idle"
            else:
                st.error("Could not extract text from this file.")

    if st.session_state.rfi_text:
        st.markdown(f"""
        <div style="background:#0d1f14;border:1px solid #10b981;border-radius:8px;
            padding:12px 16px;margin-top:8px;display:flex;align-items:center;gap:12px;">
            <div style="width:36px;height:36px;background:#10b98120;border:1px solid #10b98140;
                border-radius:6px;display:flex;align-items:center;justify-content:center;
                font-size:16px;">&#128196;</div>
            <div style="flex:1;">
                <div style="font-family:Space Grotesk,sans-serif;font-size:13px;
                    font-weight:600;color:#f8fafc;">{uploaded_file.name}</div>
                <div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#475569;">
                    {len(st.session_state.rfi_text):,} characters extracted &nbsp;&#183;&nbsp; Ready for pipeline
                </div>
            </div>
            <div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#10b981;
                font-weight:600;">&#10003; PARSED</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Preview Document Content", key="preview_btn"):
            st.code(
                st.session_state.rfi_text[:1500] + ("..." if len(st.session_state.rfi_text) > 1500 else ""),
                language="text"
            )

st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

# ── Run Button ───────────────────────────────────────────────────
section_label("02", "Execute Pipeline")

if st.session_state.rfi_text and not st.session_state.running:
    run_clicked = st.button("Launch Pipeline  &#9654;", type="primary", use_container_width=True)
else:
    run_clicked = False
    lbl = "Pipeline Running — Please Wait..." if st.session_state.running else "Upload an RFI document to begin"
    st.button(lbl, disabled=True, use_container_width=True)

# ── Live Agent Feed ──────────────────────────────────────────────
if run_clicked:
    st.session_state.running     = True
    st.session_state.results     = None
    st.session_state.rerun_count = 0
    st.session_state.show_critic = False
    st.session_state.current_req = st.session_state.rfi_text
    for k in st.session_state.agent_progress:
        st.session_state.agent_progress[k] = "idle"

    section_label("03", "Live Agent Feed")

    agent_containers = {
        "brief":   {"label": "Project Lead Agent",     "color": "#00d4ff", "lang": "markdown"},
        "stories": {"label": "Business Analyst Agent", "color": "#8b5cf6", "lang": "markdown"},
        "design":  {"label": "System Architect Agent", "color": "#14b8a6", "lang": "markdown"},
        "code":    {"label": "Developer Agent",        "color": "#f59e0b", "lang": "python"},
        "tests":   {"label": "QA Tester Agent",        "color": "#10b981", "lang": "markdown"},
    }

    placeholders = {}
    for key, info in agent_containers.items():
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e2d45;border-left:3px solid {info['color']};
            border-radius:8px;padding:8px 14px;margin-bottom:4px;">
            <span style="font-family:Space Grotesk,sans-serif;font-size:12px;
                font-weight:600;color:{info['color']};">{info['label']}</span>
        </div>
        """, unsafe_allow_html=True)
        placeholders[key] = st.empty()
        placeholders[key].markdown(
            '<span style="font-family:JetBrains Mono,monospace;font-size:12px;'
            'color:#253552;padding-left:8px;">Awaiting activation...</span>',
            unsafe_allow_html=True
        )

    output_queue   = queue.Queue()
    pipeline_done  = [False]
    pipeline_error = [None]
    final_results  = [None]

    def run_with_live(rfi_text):
        import agents.project_lead as pl
        original_safe = pl.safe_output

        def patched_safe(input_text, output_text, agent_name, is_code=False):
            result, conf = original_safe(input_text, output_text, agent_name, is_code)
            key_map = {
                "Project Lead": "brief", "BA Agent": "stories",
                "Design Agent": "design", "Developer Agent": "code",
                "Testing Agent": "tests", "Critic Agent": "review",
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

    sidebar_key_map = {
        "brief": "Project Lead", "stories": "BA Agent",
        "design": "Design Agent", "code": "Developer",
        "tests": "Tester", "review": "Critic"
    }
    completed = set()

    while not pipeline_done[0] or not output_queue.empty():
        try:
            item  = output_queue.get(timeout=1)
            key   = item["key"]
            text  = item["text"]
            if key not in completed:
                completed.add(key)
                sk = sidebar_key_map.get(key)
                if sk:
                    st.session_state.agent_progress[sk] = "done"
                if key == "review":
                    st.session_state.agent_progress["Critic"] = "done"
                    continue
                info = agent_containers.get(key, {})
                if info.get("lang") == "python":
                    placeholders[key].code(text, language="python")
                else:
                    placeholders[key].markdown(text)
        except queue.Empty:
            t.sleep(0.5)

    thread.join()

    if pipeline_error[0]:
        err = pipeline_error[0]
        st.error(f"Pipeline failed: {err}")
        if "rate_limit" in err.lower():
            st.warning("Rate limit hit — wait 60 seconds and retry.")
        st.session_state.running = False
    else:
        st.session_state.results = final_results[0]
        st.session_state.running = False
        st.rerun()

# ── Results ──────────────────────────────────────────────────────
if st.session_state.results and not st.session_state.running:
    r = st.session_state.results

    if r.get("memory_hit"):
        status_box("ChromaDB Memory Hit — Similar RFI found in vector store", "#00d4ff", "&#127775;")

    rerun_count = st.session_state.rerun_count
    if "NEEDS_IMPROVEMENT" in r.get("review", "") and rerun_count < 2:
        status_box(f"Critic flagged issues — Iteration {rerun_count + 1}/2 available", "#f59e0b", "&#9888;")
        if st.button(f"Re-run with Critic Feedback  [{rerun_count + 1}/2]", type="primary"):
            with st.spinner(f"Iteration {rerun_count + 1} — Developer improving..."):
                new_results = run_pipeline(
                    st.session_state.current_req,
                    use_feedback=r.get("critic_feedback", "")
                )
                st.session_state.results     = new_results
                st.session_state.rerun_count = rerun_count + 1
                st.session_state.show_critic = False
                st.rerun()
    elif rerun_count >= 2:
        st.success("Max iterations reached (2/2) — Final version locked in.")
    elif "APPROVE" in r.get("review", ""):
        st.success("Critic Verdict: Approved — Code quality nominal.")

    section_label("04", "Pipeline Outputs")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Project Brief",
        "User Stories",
        "System Design",
        "Source Code",
        "Test Report",
    ])

    with tab1:
        st.markdown(r.get("brief", ""))
        st.download_button("Download Brief", r.get("brief", ""), file_name="project_brief.md", key="dl_brief")

    with tab2:
        st.markdown(r.get("stories", ""))
        st.download_button("Download User Stories", r.get("stories", ""), file_name="user_stories.md", key="dl_stories")

    with tab3:
        design_text = r.get("design", "")
        if "FLOW_START" in design_text and "FLOW_END" in design_text:
            doc_part  = design_text.split("FLOW_START")[0].strip()
            flow_part = design_text.split("FLOW_START")[1].split("FLOW_END")[0].strip()
            st.markdown(doc_part)
            st.markdown("""
            <div style="font-family:Space Grotesk,sans-serif;font-size:12px;font-weight:600;
                color:#475569;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 8px 0;">
                System Flow Diagram</div>
            """, unsafe_allow_html=True)
            render_flow_diagram(flow_part)
        else:
            st.markdown(design_text)
        st.download_button("Download Design Doc", design_text, file_name="system_design.md", key="dl_design")

    with tab4:
        code_text = r.get("code", "")
        st.code(code_text, language="python")
        st.download_button("Download Source Code", code_text, file_name="generated_code.py", key="dl_code")

    with tab5:
        tests_text = r.get("tests", "")
        st.markdown(tests_text)
        st.download_button("Download Test Report", tests_text, file_name="test_report.md", key="dl_tests")

    # Critic review
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if not st.session_state.show_critic:
        if st.button("View Internal Quality Review", key="show_critic_btn"):
            st.session_state.show_critic = True
            st.rerun()
    else:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e2d45;border-top:2px solid #ec4899;
            border-radius:8px;padding:16px;margin-top:8px;">
        <div style="font-family:Space Grotesk,sans-serif;font-size:12px;font-weight:600;
            color:#ec4899;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">
            Internal Quality Review — Critic Agent</div>
        """, unsafe_allow_html=True)
        st.markdown(r.get("review", ""))
        if r.get("critic_feedback"):
            st.markdown(f"""
            <div style="background:#1a1208;border-left:3px solid #f59e0b;border-radius:0 6px 6px 0;
                padding:10px 14px;margin-top:8px;font-family:Space Grotesk,sans-serif;
                font-size:13px;color:#fbbf24;">
                <strong style="color:#f59e0b;">Feedback for Developer:</strong><br>
                {r.get('critic_feedback')}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Close Review", key="hide_critic_btn"):
            st.session_state.show_critic = False
            st.rerun()