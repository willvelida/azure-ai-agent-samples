import json
import os
from typing import List
import asyncio  # Add asyncio import

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, Field
from openai import AsyncOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.functions import KernelArguments

load_dotenv()
client = AsyncOpenAI(
    api_key=os.environ.get("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com/",
)

chat_completion_service = OpenAIChatCompletion(
    ai_model_id="gpt-4o-mini",
    async_client=client
)

class SubTask(BaseModel):
    assigned_agent: str = Field(description="The specific agent assigned to handle this subtask")
    task_details: str = Field(description="Detailed description of what needs to be done for this subtask")

class TravelPlan(BaseModel):
    main_task: str = Field(description="The overall travel request from the user")
    subtasks: List[SubTask] = Field(description="List of subtasks broken down from the main task, each assigned to a specialized agent")

AGENT_NAME = "TravelAgent"
AGENT_INSTRUCTIONS = """
    You are an planner agent.
    Your job is to decide which agents to run based on the user's request.
    Below are the available agents specialised in different tasks:
    - FlightBooking: For booking flights and providing flight information
    - HotelBooking: For booking hotels and providing hotel information
    - CarRental: For booking cars and providing car rental information
    - ActivitiesBooking: For booking activities and providing activity information
    - DestinationInfo: For providing information about destinations
    - DefaultAgent: For handling general requests
"""

# Create the prompt execution settings and configure the Pydantic model response format
settings = OpenAIChatPromptExecutionSettings(response_format=TravelPlan)

agent = ChatCompletionAgent(
    service=chat_completion_service,
    name=AGENT_NAME,
    instructions=AGENT_INSTRUCTIONS,
    arguments=KernelArguments(settings=settings)
)

# Initialize Rich console
console = Console()

async def main():
    thread: ChatHistoryAgentThread | None = None

    user_inputs = [
        "Create a travel plan for a family of 2, from Melbourne to Italy"
    ]
    
    for user_input in user_inputs:
        # Display user input in a panel
        console.print(Panel(user_input, title="User Input", border_style="blue"))
        
        # Collect the agent's response
        response = await agent.get_response(messages=user_input, thread=thread)
        thread = response.thread

        try:
            # Try to validate the response as a TravelPlan
            travel_plan = TravelPlan.model_validate(json.loads(response.message.content))

            # Display the validated model as formatted JSON
            formatted_json = travel_plan.model_dump_json(indent=4)
            console.print(Panel(
                JSON(formatted_json),
                title="Validated Travel Plan",
                border_style="green"
            ))
        except ValidationError as e:
            # Handle validation errors
            console.print(Panel(
                str(e),
                title="Validation Error",
                border_style="red"
            ))
            # Add this to see what the response contains for debugging
            console.print(Panel(
                response.content,
                title="Raw Response",
                border_style="yellow"
            ))

        console.rule()

if __name__ == "__main__":
    asyncio.run(main())