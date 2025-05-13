import os
from openai import AsyncOpenAI
import asyncio

from semantic_kernel.agents import ChatCompletionAgent, AgentGroupChat
from semantic_kernel.agents.strategies import (
    KernelFunctionSelectionStrategy,
    KernelFunctionTerminationStrategy
)
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents import AuthorRole, ChatMessageContent
from semantic_kernel.functions import KernelFunctionFromPrompt
from dotenv import load_dotenv

load_dotenv()


def create_kernel_with_chat_completion() -> Kernel:
    kernel = Kernel()

    client = AsyncOpenAI(
        api_key=os.environ["GITHUB_TOKEN"],
        base_url="https://models.inference.ai.azure.com/",
    )

    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            async_client=client
        )
    )

    return kernel

async def main():
    REVIEWER_NAME="Concierge"
    REVIEWER_INSTRUCTIONS = """
    You are an are hotel concierge who has opinions about providing the most local and authentic experiences for travelers.
    The goal is to determine if the front desk travel agent has recommended the best non-touristy experience for a traveler.
    If so, state that it is approved.
    If not, provide insight on how to refine the recommendation without using a specific example. 
    """

    agent_reviewer = ChatCompletionAgent(
        kernel=create_kernel_with_chat_completion(),
        name=REVIEWER_NAME,
        instructions=REVIEWER_INSTRUCTIONS
    )

    FRONTDESK_NAME = "FrontDesk"
    FRONTDESK_INSTRUCTIONS = """
    You are a Front Desk Travel Agent with ten years of experience and are known for brevity as you deal with many customers.
    The goal is to provide the best activities and locations for a traveler to visit.
    Only provide a single recommendation per response.
    You're laser focused on the goal at hand.
    Don't waste time with chit chat.
    Consider suggestions when refining an idea.
    """

    agent_writer = ChatCompletionAgent(
        kernel=create_kernel_with_chat_completion(),
        name=FRONTDESK_NAME,
        instructions=FRONTDESK_INSTRUCTIONS
    )

    termination_function = KernelFunctionFromPrompt(
        function_name="termination",
        prompt="""
        Determine if the recommendation process is complete.
        
        The process is complete when the Concierge provides approval for any recommendation made by the Front Desk.
        Look for phrases like "approved", "this recommendation is approved", or any clear indication that the Concierge is satisfied with the suggestion.
        
        If the Concierge has given approval in their most recent response, respond with: yes
        Otherwise, respond with: no
        
        History:
        {{$history}}
        """
    )

    selection_function = KernelFunctionFromPrompt(
        function_name="selection",
        prompt=f"""
        Determine which participant takes the next turn in a conversation based on the the most recent participant.
        State only the name of the participant to take the next turn.
        No participant should take more than one turn in a row.
        
        Choose only from these participants:
        - {REVIEWER_NAME}
        - {FRONTDESK_NAME}
        
        Always follow these rules when selecting the next participant, each conversation should be at least 4 turns:
        - After user input, it is {FRONTDESK_NAME}'s turn.
        - After {FRONTDESK_NAME} replies, it is {REVIEWER_NAME}'s turn.
        - After {REVIEWER_NAME} provides feedback, it is {FRONTDESK_NAME}'s turn.

        History:
        {{{{$history}}}}
        """
    )

    chat = AgentGroupChat(
        agents=[agent_writer, agent_reviewer],
        termination_strategy=KernelFunctionTerminationStrategy(
            agents=[agent_reviewer],
            function=termination_function,
            kernel=create_kernel_with_chat_completion(),
            result_parser=lambda result: str(result.value[0]).lower() == "yes",
            history_variable_name="history",
            maximum_iterations=10,
        ),
        selection_strategy=KernelFunctionSelectionStrategy(
            function=selection_function,
            kernel=create_kernel_with_chat_completion(),
            result_parser=lambda result: str(
                result.value[0]) if result.value is not None else FRONTDESK_NAME,
            agent_variable_name="agents",
            history_variable_name="history",
        ),
    )

    user_input = "I would like to go to Italy."

    await chat.add_chat_message(ChatMessageContent(role=AuthorRole.USER, content=user_input))
    print(f"# User: '{user_input}'")

    async for content in chat.invoke():
        print(f"# Agent - {content.name or '*'}: '{content.content}'")

    print(f"# IS COMPLETE: {chat.is_complete}")

if __name__ == "__main__":
    asyncio.run(main())