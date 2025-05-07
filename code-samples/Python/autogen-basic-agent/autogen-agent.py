import os
import asyncio
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import UserMessage
from autogen_ext.models.azure import AzureAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console

load_dotenv()
client = AzureAIChatCompletionClient(
    model="gpt-4o-mini",
    endpoint="https://models.inference.ai.azure.com",
    credential=AzureKeyCredential(os.getenv("GITHUB_TOKEN")),
    model_info={
        "json_output": True,
        "function_calling": True,
        "vision": True,
        "family": "unknown"
    },
)

agent = AssistantAgent(
    name="assistant",
    model_client=client,
    tools=[],
    system_message="You are a travel agent that plans great vacations",
)

async def main():
    try:
        # Define the query
        user_query = "Plan me a great sunny vacation"

        # Execute the agent response
        response = await agent.on_messages(
            [TextMessage(content=user_query, source="user")],
            cancellation_token=CancellationToken()
        )

        print(response)

    finally:
        await client.close()

# Start the app
if __name__ == "__main__":
    asyncio.run(main())