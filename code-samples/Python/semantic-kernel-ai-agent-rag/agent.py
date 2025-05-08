from azure.ai.projects.models import FileSearchTool, OpenAIFile, VectorStore
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread, AzureAIAgentSettings
import asyncio

async def main():
    ai_agent_settings = AzureAIAgentSettings()
    thread: AzureAIAgentThread | None = None

    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credentials=True
        ) as creds,
        AzureAIAgent.create_client(credential=creds) as client
    ):
        file: OpenAIFile = await client.agents.upload_file_and_poll(file_path="document.md", purpose="assistants")
        vectorStore: VectorStore = await client.agents.create_vector_store_and_poll(
            file_ids=[file.id], name="my_vectorstore"
        )
    
        # Define agent name and instructions
        AGENT_NAME = "RAGAgent"
        AGENT_INSTRUCTIONS = """
        You are an AI assistant designed to answer user questions using only the information retrieved from the provided document(s).

        - If a user's question cannot be answered using the retrieved context, **you must clearly respond**: 
        "I'm sorry, but the uploaded document does not contain the necessary information to answer that question."
        - Do not answer from general knowledge or reasoning. Do not make assumptions or generate hypothetical explanations.
        - Do not provide definitions, tutorials, or commentary that is not explicitly grounded in the content of the uploaded file(s).
        - If a user asks a question like "What is a Neural Network?", and this is not discussed in the uploaded document, respond as instructed above.
        - For questions that do have relevant content in the document (e.g., Contoso's travel insurance coverage), respond accurately, and cite the document explicitly.

        You must behave as if you have no external knowledge beyond what is retrieved from the uploaded document.
        """
    
        # Create file search tool with uploaded resources
        file_search = FileSearchTool(vector_store_ids=[vectorStore.id])

        # Create an agent on the Azure AI agent service with the file search tool
        agent_definition = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            tools=file_search.definitions,
            tool_resources=file_search.resources,
        )

        # Create the Azure AI Agent using the client and defintion
        agent = AzureAIAgent(
            client=client,
            definition=agent_definition
        )

        # Example user queries
        user_inputs = [
            "Can you explain Contoso's travel insurance coverage?",
            "What is a neural network"
        ]

        try:
            for user_input in user_inputs:
                print(f"# User: '{user_input}'")
                async for response in agent.invoke(messages=user_input, thread=thread):
                    print(f"# {response.name}: {response}")
                    thread = response.thread
        finally:
            # Clean up resources
            if thread:
                await thread.delete()
            await client.agents.delete_vector_store(vector_store_id=vectorStore.id)
            await client.agents.delete_file(file.id)
            await client.agents.delete_agent(agent_id=agent.id)
            print("\nCleaned up agent, thread, file, and vector store")

# Start the app
if __name__ == "__main__":
    asyncio.run(main())


