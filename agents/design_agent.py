import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def design_agent(user_stories):

    prompt = f"""
You are a Software Architect.

Using the following user stories generate a system design.

User Stories:
{user_stories}

Generate the following sections:

1. System Architecture
2. Database Schema
3. API Endpoints
4. UI Components
"""

    response = model.generate_content(prompt)

    return response.text
