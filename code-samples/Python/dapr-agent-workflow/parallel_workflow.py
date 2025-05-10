import logging
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from dapr_agents.workflow import WorkflowApp, workflow, task
from dapr.ext.workflow import DaprWorkflowContext

# load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define a structured model for a single question
class Question(BaseModel):
    """Represents a single research question."""

    text: str = Field(...,description="A research question related to the topic")

# Define a model that holds multiple questions
class Questions(BaseModel):
    """Encapsulates a list of research questions."""

    questions: List[Question] = Field(
        ..., description="A list of research questions generated for the topic."
    )

# Define workflow logic
@workflow(name="research_workflow")
def research_workflow(ctx: DaprWorkflowContext, topic: str):
    """Defines a Dapr workflow for research a given topic."""

    # Generate research questions
    questions: Questions = yield ctx.call_activity(
        generate_questions, input={"topic": topic}
    )

    # Gather information for each question in parallel
    parallel_tasks = [
        ctx.call_activity(gather_information, input={"question": q["text"]})
        for q in questions["questions"]
    ]
    research_results = yield wfapp.when_all(parallel_tasks)

    # Synthesize the results into a final report
    final_report = yield ctx.call_activity(synthesize_result,
                                           input={"topic": topic, "research_results": research_results})
    
    return final_report

@task(description="Generate 3 focused research questions about {topic}.")
def generate_questions(topic: str) -> Questions:
    """Generates three research questions related to the given topic."""
    pass

@task(description="Research information to answer this question: {question}. Provide a detailed response.")
def gather_information(question: str) -> str:
    """Fetches revelant information based on the research question provided"""
    pass

@task(description="Create a comprehensive research report on {topic} based on the following research: {research_results}")
def synthesize_result(topic: str, research_results: List[str]) -> str:
    """Synthesizes the gathered research into a structured report."""
    pass

if __name__ == "__main__":
    wfapp = WorkflowApp()

    research_topic = "The environmental impact of quantum computing"

    logging.info(f"Starting research workflow on: {research_topic}")
    results = wfapp.run_and_monitor_workflow_sync(research_workflow, input=research_topic)
    logging.info(f"\nResearch Report:\n{results}")