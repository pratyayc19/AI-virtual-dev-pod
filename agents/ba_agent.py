# agents/ba_agent.py
# Business Analyst Agent — Fixed by P1

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import chromadb
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# ChromaDB setup
client = chromadb.Client()
collection = client.get_or_create_collection(name="org_templates")

def load_templates():
    try:
        with open("templates/user_story_template.txt", "r") as f:
            user_template = f.read()
        collection.add(
            documents=[user_template],
            ids=["user_story_template"]
        )
    except Exception as e:
        print(f"Template load warning: {e}")

load_templates()

def retrieve_template(query):
    try:
        results = collection.query(query_texts=[query], n_results=1)
        return results["documents"][0][0]
    except:
        return "As a [user], I want [goal] so that [benefit]. Acceptance criteria: [criteria]"

def get_llm():
    return LLM(
        model="groq/llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

def create_ba_agent():
    return Agent(
        role="Business Analyst",
        goal="Convert business requirements into clear structured user stories",
        backstory="""You are a senior Business Analyst with 10 years of experience 
        in IT projects. You excel at breaking down complex requirements into 
        clear, actionable user stories with acceptance criteria.""",
        llm=get_llm(),
        verbose=True
    )

def run_ba_agent(requirement: str):
    template = retrieve_template("user story template")
    ba = create_ba_agent()

    task = Task(
        description=f"""
        Convert this business requirement into structured user stories.
        
        Use this template format:
        {template}
        
        REQUIREMENT: {requirement}
        
        Output JSON with this structure:
        {{
            "epic": "epic name",
            "user_stories": [
                {{
                    "story": "As a [user], I want [goal] so that [benefit]",
                    "acceptance_criteria": ["criteria 1", "criteria 2"]
                }}
            ]
        }}
        """,
        expected_output="JSON with epic and list of user stories with acceptance criteria",
        agent=ba
    )

    crew = Crew(agents=[ba], tasks=[task], verbose=True)
    result = crew.kickoff()
    return str(result)

if __name__ == "__main__":
    result = run_ba_agent("Build a student attendance management system")
    print("\n✅ USER STORIES:")
    print(result)