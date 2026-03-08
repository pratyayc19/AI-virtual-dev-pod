# Project Lead Agent - Person 1
# agents/project_lead.py
# Project Lead Agent — Person 1 (Team Lead)

from crewai import Agent, Task, Crew, Process
from crewai import LLM
from dotenv import load_dotenv
import os
import sys
from agents.ba_agent import business_analyst_agent
from agents.design_agent import design_agent


from sympy import python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def get_crewai_llm():
    return LLM(
        model="groq/llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

def create_project_lead():
    return Agent(
        role="Project Lead",
        goal="Understand business requirements and coordinate the development team to deliver software",
        backstory="""You are a senior project manager at a top IT firm. 
        You break down business requirements, assign tasks to the right team members, 
        and ensure quality delivery at every stage.""",
        llm=get_crewai_llm(),
        verbose=True
    )

def run_pipeline(business_requirement: str):
    print(f"\n🚀 Starting Virtual Dev Pod for: {business_requirement}\n")
    
    lead = create_project_lead()

    task = Task(
        description=f"""
        Analyze this business requirement and create a clear project brief:
        
        REQUIREMENT: {business_requirement}
        
        Your output should include:
        1. Project summary in simple terms
        2. Key features needed
        3. Suggested tech stack
        4. Risks or challenges to watch out for
        """,
        expected_output="A structured project brief with summary, features, tech stack and risks",
        agent=lead
    )

    crew = Crew(
        agents=[lead],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    #p2 part below
    print("\n📋 PROJECT BRIEF GENERATED:\n")
    print(result)

    # Step 2 — Business Analyst Agent
    print("\n🧠 Running Business Analyst Agent...\n")

    user_stories = business_analyst_agent(business_requirement)

    print("User Stories Generated:\n")
    print(user_stories)

    # Step 3 — Design Agent
    print("\n🏗 Running Design Agent...\n")

    system_design = design_agent(user_stories)

    print("System Design Generated:\n")
    print(system_design)



    return {
    "project_brief": result,
    "system_design": system_design
    }

if __name__ == "__main__":
    result = run_pipeline("Build a simple student attendance management system")
    print("\n✅ PROJECT BRIEF COMPLETE:")
    print(result)

