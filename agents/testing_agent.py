
from crewai import Agent, Task, LLM  # import crewai components

llm = LLM(model="groq/llama-3.1-8b-instant")  # connect to groq llama model

def create_testing_agent():
    return Agent(
        role="QA Testing Engineer",                          # agent's job title
        goal="Generate tests for code and report pass/fail results",  # what it aims to do
        backstory=(
            "You are a senior QA engineer in an AI dev pod. "
            "You receive code from the Developer Agent and test it thoroughly."
        ),                                                   # gives agent personality/context
        llm=llm,                                             # use groq llama as the brain
        verbose=True,                                        # print agent thinking steps
        allow_delegation=False,                              # agent works alone, no handoff
    )

def create_testing_task(agent, source_code):
    return Task(
        description=f"""
        You received this source code from the Developer Agent:

        {source_code}

        Your job:
        1. Write unit tests for every function.
        2. Write 2 integration tests.
        3. Test edge cases.
        4. Report results in this format:

        TEST RESULTS:
        - Test Name: <name>
          Status: PASS / FAIL
          Notes: <brief explanation>

        SUMMARY:
        - Total Tests: X
        - Passed: X
        - Failed: X
        - Coverage Estimate: X%
        """,
        expected_output="A structured test report with PASS/FAIL results and summary.",  # what we expect back
        agent=agent,                                         # assign task to testing agent
    )
