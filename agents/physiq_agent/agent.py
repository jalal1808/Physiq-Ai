import os
from dotenv import load_dotenv
load_dotenv()
from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from . import prompt

# os.environ['GROQ_API_KEY']

mcp_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[os.path.abspath("kb_server.py")],
        )
    )
)

nutritionist = Agent(
    name="Nutritionist",
    model="gemini-2.5-flash", 
    instruction="food",
    tools=[mcp_tools]
)

sleep_guardian = Agent(
    name="SleepGuardian",
    model="gemini-2.5-flash",
    instruction="sleep",
    tools=[mcp_tools]
)

fitness_coach = Agent(
    name="FitnessCoach",
    model="gemini-2.5-flash", 
    instruction="fitness",
    tools=[mcp_tools]
)

medical_assistant = Agent(
    name="MedicalAssistant",
    model="gemini-2.5-flash",
    instruction="medical_assistant",
    tools=[mcp_tools]
)

coordinator = Agent(
    name="HealthSystem",
    model="gemini-2.5-flash",
    instruction="coordination",
    sub_agents=[sleep_guardian, fitness_coach, medical_assistant, nutritionist]
)

root_agent = SequentialAgent(
    name="PhysiqAgent",
    description=(
        "PhysiqAgent is the primary entry point for users. "
        "It delegates all user requests to the HealthSystem coordinator, "
        "which routes them to the appropriate health specialist agent."
    ),
    sub_agents=[coordinator],
)


from . import medical_guard

def run_physiq(message: str, history=None):
    if history is None:
        history = []

    response = root_agent.run(
        message=message,
        context={"history": history}
    )

    # Apply medical safety
    safe_response = medical_guard(response)

    return safe_response
