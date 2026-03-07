# Bedrock LLM Client - Person 1

# cloud/bedrock_client.py
# Shared LLM Client — Person 1 (Team Lead)
# Used by ALL agents in the project

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm():
    """Returns the shared LLM instance used by all agents."""
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

# Test it directly
if __name__ == "__main__":
    llm = get_llm()
    response = llm.invoke("Say hello from the AI Virtual Dev Pod!")
    print(response.content)

