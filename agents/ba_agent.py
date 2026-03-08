import google.generativeai as genai
import chromadb
import os


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


client = chromadb.Client()

collection = client.get_or_create_collection(name="org_templates")


def load_templates():

    with open("templates/user_story_template.txt","r") as f:
        user_template = f.read()

    with open("templates/design_template.txt","r") as f:
        design_template = f.read()

    collection.add(
        documents=[user_template, design_template],
        ids=["user_story_template","design_template"]
    )


load_templates()


def retrieve_template(query):

    results = collection.query(
        query_texts=[query],
        n_results=1
    )

    return results["documents"][0][0]


def business_analyst_agent(requirement):

    template = retrieve_template("user story template")

    prompt = f"""
You are a Business Analyst.

Use this template:

{template}

Convert this requirement into JSON user stories.

Requirement:
{requirement}

Return JSON format:

{{
 "epic":"",
 "user_stories":[
   {{
     "story":"",
     "acceptance_criteria":[]
   }}
 ]
}}
"""

    response = model.generate_content(prompt)

    return response.text
