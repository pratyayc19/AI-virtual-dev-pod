# Project Lead Agent - Person 1
# agents/project_lead.py
# Project Lead Agent — Person 1 (Team Lead)
# agents/project_lead.py
# Project Lead Agent — Full Pipeline — Person 1
# agents/project_lead.py
# Project Lead Agent — Full Pipeline — Person 1

from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def get_llm():
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

def run_pipeline(business_requirement: str):
    print(f"\n🚀 Starting Virtual Dev Pod for: {business_requirement}\n")

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

    task_dev = Task(
        description="""
        Based on the system design, generate Python source code.
        Write one main class with 3-4 key methods.
        Include inline comments.
        Keep code under 50 lines.
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
        Keep response concise — maximum 150 words.
        """,
        expected_output="Code review with quality score and verdict",
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

    return {
        "brief":   str(task_lead.output),
        "stories": str(task_ba.output),
        "design":  str(task_design.output),
        "code":    str(task_dev.output),
        "tests":   str(task_test.output),
        "review":  str(task_critic.output),
        "final":   str(result)
    }

if __name__ == "__main__":
    results = run_pipeline("Build a simple student attendance management system")
    print("\n✅ PIPELINE COMPLETE!")
    print("FINAL REVIEW:", results["review"])