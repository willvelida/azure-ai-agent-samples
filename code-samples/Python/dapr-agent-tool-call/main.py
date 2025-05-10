import asyncio
from weather_tools import tools
from dapr_agents import Agent
from dotenv import load_dotenv
from dapr_agents.memory import ConversationDaprStateMemory

load_dotenv()

AIAgent = Agent(
    name="Stevie",
    role="Weather Assistant",
    goal="Assist Humans with weather related tasks.",
    instructions=[
        "Get accurate weather information",
        "From time to time, you can also jump after answering the weather question."
    ],
    memory=ConversationDaprStateMemory(store_name="historystore",session_id="some-id"),
    tools=tools
)

# Wrap your async call
async def main():
    await AIAgent.run("What is the weather in Melbourne, Perth, and Canberra?")

    # View history after first interaction
    print("Chat history after first interaction:")
    print(AIAgent.chat_history)

    # Second interaction (agent will remember the first one)
    await AIAgent.run("How about in Sydney?")

    # View updated history
    print("Chat history after second interaction:")
    print(AIAgent.chat_history)

    # Reset memory
    AIAgent.reset_memory()
    print("Chat history after reset:")
    print(AIAgent.chat_history) # Should be empty

if __name__ == "__main__":
    asyncio.run(main())