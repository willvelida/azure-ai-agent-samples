import asyncio
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Union
import json
import os
from typing import Optional
from pprint import pprint
from autogen_core.models import UserMessage, SystemMessage, AssistantMessage
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

class AgentEnum(str, Enum):
    FlightBooking = "flight_booking"
    HotelBooking = "hotel_booking"
    CarRental = "car_rental"
    ActivitiesBooking = "activities_booking"
    DestinationInfo = "destination_info"
    DefaultAgent = "default_agent"
    GroupChatManager = "group_chat_manager"

class TravelSubTask(BaseModel):
    task_details: str
    assigned_agent: AgentEnum

class TravelPlan(BaseModel):
    main_task: str
    subtasks: List[TravelSubTask]
    is_greeting: bool

client = AzureAIChatCompletionClient(
    model="gpt-4o-mini",
    endpoint="https://models.inference.ai.azure.com",
    credential=AzureKeyCredential(os.getenv("GITHUB_TOKEN")),
    model_info={
        "json_output": False,
        "function_calling": True,
        "vision": True,
        "family": "unknown",
        "structured_output": True
    },
)

async def main():
    try:
    # Define the user message
        messages = [
            SystemMessage(content="""You are an planner agent.
            Your job is to decide which agents to run based on the user's request.
                            Provide your response in JSON format with the following structure:
        {'main_task': 'Plan a family trip from Singapore to Melbourne.',
        'subtasks': [{'assigned_agent': 'flight_booking',
                    'task_details': 'Book round-trip flights from Singapore to '
                                    'Melbourne.'}
            Below are the available agents specialised in different tasks:
            - FlightBooking: For booking flights and providing flight information
            - HotelBooking: For booking hotels and providing hotel information
            - CarRental: For booking cars and providing car rental information
            - ActivitiesBooking: For booking activities and providing activity information
            - DestinationInfo: For providing information about destinations
            - DefaultAgent: For handling general requests""", source="system"),
            UserMessage(
                content="Create a travel plan for a family of 2 from Melbourne to Florence", source="user"),
        ]

        response = await client.create(messages=messages, extra_create_args={"response_format": 'json_object'})

        response_content: Optional[str] = response.content if isinstance(
            response.content, str
        ) else None
        if response_content is None:
            raise ValueError("Response content is not a valid JSON string")
            
        pprint(json.loads(response_content))
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())