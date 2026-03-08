# agents/design_agent.py
# Design Agent — Fixed by P1

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def get_llm():
    return LLM(
        model="groq/llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

def create_design_agent():
    return Agent(
        role="Software Architect",
        goal="Create detailed system design from user stories",
        backstory="""You are a senior Software Architect with expertise in 
        designing scalable systems. You create clear architecture docs, 
        database schemas and API contracts.""",
        llm=get_llm(),
        verbose=True
    )

def run_design_agent(user_stories: str):
    designer = create_design_agent()

    task = Task(
        description=f"""
        Create a complete system design based on these user stories:
        
        USER STORIES: {user_stories}
        
        Your output must include:
        1. System Architecture (components and how they connect)
        2. Database Schema (tables, fields, relationships)
        3. API Endpoints (method, path, description)
        4. UI Components (main screens/pages needed)
        """,
        expected_output="Complete system design with architecture, schema, APIs and UI components",
        agent=designer
    )

    crew = Crew(agents=[designer], tasks=[task], verbose=True)
    result = crew.kickoff()
    return str(result)

if __name__ == "__main__":
    result = run_design_agent("User can login, mark attendance, view reports")
    print("\n✅ SYSTEM DESIGN:")
    print(result)