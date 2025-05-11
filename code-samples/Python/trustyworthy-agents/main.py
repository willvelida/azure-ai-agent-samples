import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = ChatCompletionsClient(endpoint=endpoint,credential=AzureKeyCredential(token))

def main():
    role = "gym instructor"
    company = "Velocity Sports"
    responsibility = "improving client's fitness and health"

    response = client.complete(
        messages=[
            SystemMessage(content="""You are an expert at creating AI agent assistant.
                          You will be provided a company name, role, responsibilities and other information that
                          you will use to provide a system prompt for. To create the system prompt, be descriptive as possible
                          and provide a structure that a system using an LLM can better understand the role and responsibilities of the AI assistant."""),
                          UserMessage(content=f"You are {role} at {company} that is responsible for {responsibility}"),
        ],
        model=model_name,
        temperature=1.,
        max_tokens=1000,
        top_p=1.
    )

    print(response.choices[0].message.content)

if __name__ == '__main__':
    main()