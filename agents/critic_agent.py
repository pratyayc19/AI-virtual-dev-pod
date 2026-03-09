# agents/critic_agent.py
# Self-Critic Agent — Built by P1 (Innovation)

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def get_llm():
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

def create_critic_agent():
    return Agent(
        role="Senior Code Reviewer",
        goal="Evaluate code quality and provide structured improvement feedback",
        backstory="""You are a strict but fair senior code reviewer with expertise 
        in software quality. You analyze code against best practices, security 
        standards, and test results to produce actionable improvement feedback.""",
        llm=get_llm(),
        verbose=True
    )

def run_critic_agent(source_code: str, test_results: str, iteration: int = 1):
    critic = create_critic_agent()

    task = Task(
        description=f"""
        Review this code (Iteration {iteration}) and evaluate its quality.
        
        SOURCE CODE:
        {source_code}
        
        TEST RESULTS:
        {test_results}
        
        Provide your evaluation in this EXACT format:
        
        QUALITY SCORE: [0-100]
        
        STRENGTHS:
        - [strength 1]
        - [strength 2]
        
        ISSUES FOUND:
        - [issue 1 with specific fix suggestion]
        - [issue 2 with specific fix suggestion]
        
        VERDICT: [APPROVE / NEEDS_IMPROVEMENT]
        
        FEEDBACK FOR DEVELOPER:
        [Specific actionable instructions for the next iteration]
        """,
        expected_output="Structured code review with quality score, issues, verdict and feedback",
        agent=critic
    )

    crew = Crew(agents=[critic], tasks=[task], verbose=True)
    result = crew.kickoff()
    return str(result)

def run_feedback_loop(design_doc: str, test_results: str, max_iterations: int = 2):
    """Run the full self-critic improvement loop."""
    from agents.developer_agent import run_developer_agent

    print(f"\n🔁 Starting Self-Critic Feedback Loop (max {max_iterations} iterations)\n")

    feedback = None
    final_code = None

    for i in range(1, max_iterations + 1):
        print(f"\n--- Iteration {i} ---")

        # Developer generates/improves code
        code = run_developer_agent(design_doc, feedback)
        final_code = code

        # Critic evaluates
        review = run_critic_agent(code, test_results, i)
        print(f"\n📊 Critic Review (Iteration {i}):\n{review}")

        # Check verdict
        if "APPROVE" in review and "NEEDS_IMPROVEMENT" not in review:
            print(f"\n✅ Code APPROVED after {i} iteration(s)!")
            break

        # Extract feedback for next iteration
        if "FEEDBACK FOR DEVELOPER:" in review:
            feedback = review.split("FEEDBACK FOR DEVELOPER:")[-1].strip()

    return final_code, review

if __name__ == "__main__":
    sample_design = "Build a student attendance system with mark_attendance() and get_report() functions"
    sample_tests = "Test 1: mark_attendance() - PASS\nTest 2: get_report() - FAIL (returns None)"

    final_code, final_review = run_feedback_loop(sample_design, sample_tests)
    print("\n✅ FINAL CODE AFTER CRITIC LOOP:")
    print(final_code)


