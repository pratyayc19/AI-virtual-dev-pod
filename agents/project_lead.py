# agents/project_lead.py
# Orchestrator + Pipeline Runner — Person 1

import os, time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq

from responsible_ai.guardrails import apply_guardrails, redact_pii, check_input
from memory.chroma_store import save_artifact, get_artifact

load_dotenv()

llm = ChatGroq(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

# ── Responsible AI wrapper ─────────────────────────────────────────
def safe_output(input_text, output_text, agent_name, is_code=False):
    output_text = redact_pii(output_text)
    if not is_code:
        flagged, reason = apply_guardrails(input_text, output_text)
        if flagged:
            print(f"⚠️  {agent_name} output flagged: {reason}")
            return f"[Output filtered by Responsible AI: {reason}]", 0
    words = output_text.split()
    conf  = min(100, max(40, len(words) * 2)) if words else 0
    return output_text, conf

# ── Main Pipeline ──────────────────────────────────────────────────
def run_pipeline(business_requirement, use_feedback=None):

    # 1. Input safety check
    is_safe, reason = check_input(business_requirement)
    if not is_safe:
        return {
            "brief": f"🚫 Blocked by Responsible AI: {reason}",
            "stories": "", "design": "", "code": "",
            "tests": "", "review": "", "final": "",
            "memory_hit": False, "past_result": None,
            "critic_feedback": "",
            "conf_lead": 0, "conf_ba": 0, "conf_design": 0,
            "conf_dev": 0, "conf_test": 0, "conf_critic": 0,
        }

    # 2. Memory check
    memory_hit  = False
    past_result = None
    try:
        past = get_artifact(f"req_{hash(business_requirement) % 100000}")
        if past:
            memory_hit  = True
            past_result = past
            print("🧠 Memory Hit! Found similar past requirement.")
    except Exception as e:
        print(f"Memory check warning: {e}")

    # 3. Define agents
    lead = Agent(
        role="Project Lead",
        goal="Analyze RFI documents and create concise project briefs",
        backstory="Senior PM who converts business requirements into actionable plans",
        llm=llm, verbose=True, allow_delegation=False
    )
    ba = Agent(
        role="Business Analyst",
        goal="Convert project briefs into structured user stories",
        backstory="Expert BA who writes clear user stories with acceptance criteria",
        llm=llm, verbose=True, allow_delegation=False
    )
    designer = Agent(
        role="System Architect",
        goal="Create concise system designs from user stories",
        backstory="Experienced architect who designs clean, scalable systems",
        llm=llm, verbose=True, allow_delegation=False
    )
    developer = Agent(
        role="Senior Developer",
        goal="Write clean Python code from system designs",
        backstory="Expert Python developer who writes readable, well-commented code",
        llm=llm, verbose=True, allow_delegation=False
    )
    tester = Agent(
        role="QA Engineer",
        goal="Write and run test cases for source code",
        backstory="Thorough QA engineer who finds bugs and validates functionality",
        llm=llm, verbose=True, allow_delegation=False
    )
    critic = Agent(
        role="Code Reviewer",
        goal="Review code quality and provide actionable improvement feedback",
        backstory="Senior code reviewer who ensures production-grade quality",
        llm=llm, verbose=True, allow_delegation=False
    )

    # 4. Live output collector
    live_outputs = {}

    def make_callback(agent_name, key):
        def callback(output):
            live_outputs[key] = str(output)
            print(f"\n✅ {agent_name} completed!\n")
        return callback

    # 5. Define tasks
    task_lead = Task(
        description=f"""
        Analyze this RFI document and create a project brief:
        REQUIREMENT: {business_requirement}
        Include:
        1. Project summary
        2. Key features
        3. Recommended tech stack
        4. Risks and constraints
        Keep response concise — maximum 200 words.
        """,
        expected_output="A concise project brief with summary, features, tech stack and risks",
        agent=lead,
        callback=make_callback("Project Lead", "brief")
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
        agent=ba,
        callback=make_callback("BA Agent", "stories")
    )

    task_design = Task(
        description="""
        Based on the user stories, create a system design with a flowchart.

        Your response must have TWO sections:

        SECTION 1 — DESIGN DOCUMENT:
        1. Main components (2-3 only)
        2. Database tables (key fields only)
        3. Key API endpoints (3-4 max)

        SECTION 2 — MERMAID FLOWCHART:
        Write a Mermaid flowchart showing the system flow.
        It MUST start with exactly this line: ```mermaid
        And end with exactly: ```
        Use flowchart TD direction.
        Show the main user actions and system responses.

        Example format:
```mermaid
        flowchart TD
            A[User Login] --> B{Authenticated?}
            B -->|Yes| C[Dashboard]
            B -->|No| D[Show Error]
            C --> E[Mark Attendance]
            E --> F[(Database)]
```
        """,
        expected_output="Design document with components, schema, APIs and a Mermaid flowchart",
        agent=designer,
        context=[task_ba],
        callback=make_callback("Design Agent", "design")
    )

    feedback_note = ""
    if use_feedback:
        feedback_note = f"\nIMPORTANT: Critic feedback to fix:\n{use_feedback}\n"

    task_dev = Task(
        description=f"""
        Based on the system design, generate complete production-ready Python source code.
        {feedback_note}

        Requirements:
        1. Use SQLite as the real database (import sqlite3)
        2. Create tables in __init__ using CREATE TABLE IF NOT EXISTS
        3. All data must be saved to and retrieved from the database — NO in-memory lists
        4. Include proper error handling with try/except blocks
        5. Write a complete working class with all key methods from the design
        6. Include inline comments explaining each method
        7. At the bottom write: if __name__ == "__main__": with a working demo

        The code must be fully runnable — someone should be able to copy it,
        run it with just Python installed, and see real output.
        """,
        expected_output="Complete production-ready Python code with SQLite database integration",
        agent=developer,
        context=[task_design],
        callback=make_callback("Developer Agent", "code")
    )

    task_test = Task(
        description="""
        Write 5 test cases for the code using Python's unittest framework.

        Requirements:
        1. Use unittest.TestCase
        2. Use an in-memory SQLite database for tests (:memory:)
        3. Test: database creation, insert, retrieve, edge cases, error handling
        4. Each test must have a clear assert statement
        5. Include setUp() to initialize the system before each test

        After the test class write the actual results:
        TEST RESULTS:
        - Test Name: [name] | Status: PASS/FAIL | Notes: [notes]
        SUMMARY: Total: 5 | Passed: X | Failed: X | Coverage: X%
        """,
        expected_output="Complete unittest test class with 5 tests and results summary",
        agent=tester,
        context=[task_dev],
        callback=make_callback("Testing Agent", "tests")
    )

    task_critic = Task(
        description="""
        Review the code and test results.
        Format your response exactly as:
        QUALITY SCORE: [0-100]
        STRENGTHS:
        - [strength 1]
        - [strength 2]
        ISSUES:
        - [issue 1 with fix]
        - [issue 2 with fix]
        VERDICT: APPROVE / NEEDS_IMPROVEMENT
        FEEDBACK FOR DEVELOPER: [specific fixes needed]
        Keep response concise — maximum 150 words.
        """,
        expected_output="Code review with quality score, verdict and developer feedback",
        agent=critic,
        context=[task_dev, task_test],
        callback=make_callback("Critic Agent", "review")
    )

    # 6. Run crew
    crew = Crew(
        agents=[lead, ba, designer, developer, tester, critic],
        tasks=[task_lead, task_ba, task_design, task_dev, task_test, task_critic],
        process=Process.sequential,
        verbose=True
    )

    time.sleep(2)
    crew.kickoff()

    # 7. Responsible AI on all outputs
    print("\n🛡️ Running Responsible AI checks on all outputs...\n")
    brief,   conf_lead   = safe_output(business_requirement, live_outputs.get("brief",   ""), "Project Lead",    is_code=True)
    stories, conf_ba     = safe_output(business_requirement, live_outputs.get("stories", ""), "BA Agent",        is_code=True)
    design,  conf_design = safe_output(business_requirement, live_outputs.get("design",  ""), "Design Agent",    is_code=True)
    code,    conf_dev    = safe_output(business_requirement, live_outputs.get("code",    ""), "Developer Agent", is_code=True)
    tests,   conf_test   = safe_output(business_requirement, live_outputs.get("tests",   ""), "Testing Agent",   is_code=True)
    review,  conf_critic = safe_output(business_requirement, live_outputs.get("review",  ""), "Critic Agent",    is_code=True)
    print("\n✅ All outputs passed Responsible AI checks!\n")

    # 8. Save to memory
    try:
        save_artifact(
            artifact_id=f"req_{hash(business_requirement) % 100000}",
            content=f"REQUIREMENT: {business_requirement}\nBRIEF: {brief}\nCODE: {code}",
            metadata={"type": "pipeline_run", "requirement": business_requirement[:100]}
        )
        print("🧠 Result saved to ChromaDB memory!\n")
    except Exception as e:
        print(f"Memory save warning: {e}")

    # 9. Extract critic feedback
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
        "final":           str(review),
        "memory_hit":      memory_hit,
        "past_result":     past_result,
        "critic_feedback": critic_feedback,
        "conf_lead":       conf_lead,
        "conf_ba":         conf_ba,
        "conf_design":     conf_design,
        "conf_dev":        conf_dev,
        "conf_test":       conf_test,
        "conf_critic":     conf_critic,
    }


# ── Local test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Testing Normal Requirement ===")
    result = run_pipeline("Build a student attendance system with QR code scanning")
    print("\n--- PROJECT BRIEF ---")
    print(result["brief"])
    print("\n--- CRITIC REVIEW ---")
    print(result["review"])

    print("\n=== Testing Unsafe Requirement ===")
    result2 = run_pipeline("Hack into the student database and steal records")
    print(result2["brief"])