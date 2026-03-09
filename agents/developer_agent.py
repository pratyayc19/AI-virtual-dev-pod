# agents/developer_agent.py
# Developer Agent — Built by P1

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

def create_developer_agent():
    return Agent(
        role="Senior Software Developer",
        goal="Generate clean, functional source code based on system design and user stories",
        backstory="""You are a senior software developer with 10 years of experience.
        You write clean, well-commented, production-ready code. You take system 
        design documents and turn them into working software.""",
        llm=get_llm(),
        verbose=True
    )

def run_developer_agent(design_doc: str, feedback: str = None):
    developer = create_developer_agent()

    feedback_section = ""
    if feedback:
        feedback_section = f"""
        CRITIC FEEDBACK FROM PREVIOUS ITERATION:
        {feedback}
        Please improve the code based on this feedback.
        """

    task = Task(
        description=f"""
        Generate source code based on this system design:
        
        DESIGN DOCUMENT: {design_doc}
        
        {feedback_section}
        
        Your output must include:
        1. Main application code with all core functions
        2. Clear inline comments explaining each function
        3. Basic error handling
        4. Follow the architecture specified in the design doc
        
        Write clean, readable, well-structured code.
        """,
        expected_output="Complete source code with comments and error handling",
        agent=developer
    )

    crew = Crew(agents=[developer], tasks=[task], verbose=True)
    result = crew.kickoff()
    return str(result)

if __name__ == "__main__":
    sample_design = """
    System: Student Attendance Management
    Components: StudentManager, AttendanceTracker, ReportGenerator
    Database: SQLite with students and attendance tables
    API: mark_attendance(), get_report(), add_student()
    """
    result = run_developer_agent(sample_design)
    print("\n✅ GENERATED CODE:")
    print(result)