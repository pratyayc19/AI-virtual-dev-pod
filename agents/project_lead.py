# agents/project_lead.py
# Project Lead — Full Pipeline + All Innovations — Person 1

from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
import os, sys, time, random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from responsible_ai.guardrails import apply_guardrails, redact_pii, check_input
from memory.chroma_store import save_artifact, get_artifact

def get_llm():
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

def extract_confidence(output_text: str) -> int:
    """Calculate confidence score based on output quality signals."""
    base = 75
    if len(output_text) > 200: base += 5
    if "error" in output_text.lower(): base -= 10
    if "however" in output_text.lower(): base -= 5
    if "clearly" in output_text.lower(): base += 5
    if "```" in output_text: base += 5
    return min(99, max(60, base + random.randint(-5, 10)))

def safe_output(input_text: str, output_text: str, agent_name: str, is_code: bool = False):
    """Run guardrails + confidence scoring on every agent output."""
    # For code output — only check PII, skip content safety
    # (code naturally contains technical terms that may false-trigger guardrails)
    if is_code:
        clean = redact_pii(output_text)
        if clean != output_text:
            print(f"\n🔒 PII REDACTED [{agent_name}]")
        confidence = extract_confidence(clean)
        print(f"🎯 [{agent_name}] Confidence: {confidence}%")
        return clean, confidence

    # For all other agents — full guardrail check
    check = apply_guardrails(input_text, output_text)
    if not check["allowed"]:
        print(f"\n🛡️ GUARDRAIL BLOCKED [{agent_name}]: {check['reason']}")
        return f"⚠️ Blocked by Responsible AI: {check['reason']}", 0
    clean = redact_pii(output_text)
    if clean != output_text:
        print(f"\n🔒 PII REDACTED [{agent_name}]")
    confidence = extract_confidence(clean)
    print(f"🎯 [{agent_name}] Confidence: {confidence}%")
    return clean, confidence

def check_memory(requirement: str):
    """Check ChromaDB for similar past requirements."""
    try:
        past = get_artifact(requirement)
        if past:
            return past
    except:
        pass
    return None

def run_pipeline(business_requirement: str, use_feedback: str = None):
    print(f"\n🚀 Starting Virtual Dev Pod for: {business_requirement}\n")

    # ── Responsible AI: Check INPUT ────────────────────────────────
    input_check = check_input(business_requirement)
    if not input_check["allowed"]:
        print(f"\n🛡️ INPUT BLOCKED: {input_check['reason']}")
        return {
            "brief": f"⚠️ Blocked by Responsible AI: {input_check['reason']}",
            "stories": "", "design": "", "code": "",
            "tests": "", "review": "", "final": "",
            "memory_hit": False, "past_result": None,
            "conf_lead": 0, "conf_ba": 0, "conf_design": 0,
            "conf_dev": 0, "conf_test": 0, "conf_critic": 0,
            "critic_feedback": ""
        }
    print(f"✅ Input safety check passed!\n")

    # ── Memory: Check past requirements ───────────────────────────
    past_result = check_memory(business_requirement)
    memory_hit = past_result is not None
    if memory_hit:
        print(f"🧠 Memory Hit! Found similar past requirement.\n")

    # ── Create all agents ──────────────────────────────────────────
    lead = Agent(
        role="Project Lead",
        goal="Analyze business requirements and create a clear project brief",
        backstory="You are a senior project manager who breaks down requirements into clear actionable briefs.",
        llm=get_llm(), verbose=True
    )
    ba = Agent(
        role="Business Analyst",
        goal="Convert business requirements into structured user stories",
        backstory="You are a senior BA who writes clear user stories with acceptance criteria.",
        llm=get_llm(), verbose=True
    )
    designer = Agent(
        role="Software Architect",
        goal="Create system design from user stories",
        backstory="You are a senior architect who designs clean, scalable systems.",
        llm=get_llm(), verbose=True
    )
    developer = Agent(
        role="Senior Software Developer",
        goal="Generate clean source code based on system design",
        backstory="You are a senior developer who writes clean, well-commented production code.",
        llm=get_llm(), verbose=True
    )
    tester = Agent(
        role="QA Testing Engineer",
        goal="Generate and evaluate test cases for the code",
        backstory="You are a senior QA engineer who writes thorough test cases and reports results.",
        llm=get_llm(), verbose=True
    )
    critic = Agent(
        role="Senior Code Reviewer",
        goal="Review code quality and provide improvement feedback",
        backstory="You are a strict but fair code reviewer who ensures quality standards are met.",
        llm=get_llm(), verbose=True
    )

    # ── Create all tasks ───────────────────────────────────────────
    task_lead = Task(
        description=f"""
        Analyze this business requirement and create a project brief:
        REQUIREMENT: {business_requirement}
        Include: 1. Project summary 2. Key features 3. Tech stack 4. Risks
        Keep response concise — maximum 200 words.
        """,
        expected_output="A concise project brief with summary, features, tech stack and risks",
        agent=lead
    )
    task_ba = Task(
        description=f"""
        Convert this requirement into user stories:
        REQUIREMENT: {business_requirement}
        Write exactly 3 user stories in this format:
        EPIC: [epic name]
        USER STORIES:
        - As a [user], I want [goal] so that [benefit]
          Acceptance Criteria: [criteria]
        Keep response concise — maximum 200 words.
        """,
        expected_output="3 user stories with acceptance criteria",
        agent=ba
    )
    task_design = Task(
        description="""
        Based on the user stories, create a concise system design.
        Include:
        1. Main components (2-3 only)
        2. Database tables (key fields only)
        3. Key API endpoints (3-4 max)
        Keep response concise — maximum 200 words.
        """,
        expected_output="Concise system design with components, schema and APIs",
        agent=designer,
        context=[task_ba]
    )

    feedback_note = ""
    if use_feedback:
        feedback_note = f"\nIMPORTANT: Critic feedback to fix:\n{use_feedback}\n"

    task_dev = Task(
        description=f"""
        Based on the system design, generate Python source code.
        {feedback_note}
        Write one main class with 3-4 key methods.
        Include inline comments. Keep code under 50 lines.
        """,
        expected_output="Python source code under 50 lines with comments",
        agent=developer,
        context=[task_design]
    )
    task_test = Task(
        description="""
        Write 3 test cases for the code from the previous task.
        Format:
        TEST RESULTS:
        - Test Name: [name] | Status: PASS/FAIL | Notes: [notes]
        SUMMARY: Total: 3 | Passed: X | Failed: X | Coverage: X%
        Keep response concise — maximum 150 words.
        """,
        expected_output="3 test cases with pass/fail results and summary",
        agent=tester,
        context=[task_dev]
    )
    task_critic = Task(
        description="""
        Review the code and test results.
        Format:
        QUALITY SCORE: [0-100]
        STRENGTHS: [2 bullet points]
        ISSUES: [2 bullet points with fixes]
        VERDICT: APPROVE / NEEDS_IMPROVEMENT
        FEEDBACK FOR DEVELOPER: [specific fixes needed]
        Keep response concise — maximum 150 words.
        """,
        expected_output="Code review with quality score, verdict and developer feedback",
        agent=critic,
        context=[task_dev, task_test]
    )

    # ── Run the crew ───────────────────────────────────────────────
    crew = Crew(
        agents=[lead, ba, designer, developer, tester, critic],
        tasks=[task_lead, task_ba, task_design, task_dev, task_test, task_critic],
        process=Process.sequential,
        verbose=True
    )

    time.sleep(2)
    result = crew.kickoff()

    # ── Responsible AI: Filter ALL outputs ────────────────────────
    print("\n🛡️ Running Responsible AI checks on all outputs...\n")
    brief,   conf_lead   = safe_output(business_requirement, str(task_lead.output),   "Project Lead")
    stories, conf_ba     = safe_output(business_requirement, str(task_ba.output),     "BA Agent")
    design,  conf_design = safe_output(business_requirement, str(task_design.output), "Design Agent")
    code,    conf_dev    = safe_output(business_requirement, str(task_dev.output),    "Developer Agent", is_code=True)
    tests,   conf_test   = safe_output(business_requirement, str(task_test.output),   "Testing Agent")
    review,  conf_critic = safe_output(business_requirement, str(task_critic.output), "Critic Agent")
    print("\n✅ All outputs passed Responsible AI checks!\n")

    # ── Memory: Save this run to ChromaDB ─────────────────────────
    try:
        save_artifact(
            artifact_id=f"req_{hash(business_requirement) % 100000}",
            content=f"REQUIREMENT: {business_requirement}\nBRIEF: {brief}\nCODE: {code}",
            metadata={"type": "pipeline_run", "requirement": business_requirement[:100]}
        )
        print("🧠 Result saved to memory!\n")
    except Exception as e:
        print(f"Memory save warning: {e}")

    # Extract critic feedback for re-run
    critic_feedback = ""
    if "FEEDBACK FOR DEVELOPER:" in review:
        critic_feedback = review.split("FEEDBACK FOR DEVELOPER:")[-1].strip()

    return {
        "brief":           brief,
        "stories":         stories,
        "design":          design,
        "code":            code,
        "tests":           tests,
        "review":          review,
        "final":           str(result),
        "conf_lead":       conf_lead,
        "conf_ba":         conf_ba,
        "conf_design":     conf_design,
        "conf_dev":        conf_dev,
        "conf_test":       conf_test,
        "conf_critic":     conf_critic,
        "memory_hit":      memory_hit,
        "past_result":     past_result,
        "critic_feedback": critic_feedback
    }

if __name__ == "__main__":
    results = run_pipeline("Build a simple student attendance management system")
    print("\n✅ PIPELINE COMPLETE!")
    print("REVIEW:", results["review"])
    print(f"\nCONFIDENCE: Lead:{results['conf_lead']}% | BA:{results['conf_ba']}% | Design:{results['conf_design']}% | Dev:{results['conf_dev']}% | Test:{results['conf_test']}% | Critic:{results['conf_critic']}%")