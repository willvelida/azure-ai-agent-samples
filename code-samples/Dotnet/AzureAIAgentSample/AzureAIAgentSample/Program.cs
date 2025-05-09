// See https://aka.ms/new-console-template for more information
using Azure;
using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Extensions.Configuration;

Console.WriteLine("Hello, World!");
var config = new ConfigurationBuilder()
    .AddUserSecrets<Program>()
    .Build();

var connectionString = config["PROJECT_CONNECTION_STRING"];

AgentsClient agentsClient = new AgentsClient(connectionString, new AzureCliCredential());

// Create an Agent
Response<Agent> agentResponse = await agentsClient.CreateAgentAsync(
    model: "gpt-4o-mini",
    name: "My Agent",
    instructions: "You are a helpful agent",
    tools: new List<ToolDefinition>
    {
        new CodeInterpreterToolDefinition()
    });

Agent agent = agentResponse.Value;

Response<PageableList<Agent>> agentListResponse = await agentsClient.GetAgentsAsync();

// Create a thread
Response<AgentThread> threadResponse = await agentsClient.CreateThreadAsync();
AgentThread thread = threadResponse.Value;

// Add a message to the thread
Response<ThreadMessage> messageResponse = await agentsClient.CreateMessageAsync(
    thread.Id,
    MessageRole.User,
    "I need to solve the equation `x^2 + 2x + 1 = 0`. Can you help me please?");
ThreadMessage message = messageResponse.Value;

Response<PageableList<ThreadMessage>> messagesListResponse = await agentsClient.GetMessagesAsync(thread.Id);

// Run the agent
Response<ThreadRun> runResponse = await agentsClient.CreateRunAsync(
    thread.Id,
    agent.Id,
    additionalInstructions: "Please provide a step-by-step solution to the equation.");
ThreadRun run = runResponse.Value;

do
{
    await Task.Delay(TimeSpan.FromMilliseconds(500));
    runResponse = await agentsClient.GetRunAsync(thread.Id, runResponse.Value.Id);
} while (runResponse.Value.Status == RunStatus.Queued || runResponse.Value.Status == RunStatus.InProgress);

Response<PageableList<ThreadMessage>> afterRunMessagesResponses = await agentsClient.GetMessagesAsync(thread.Id);
IReadOnlyList<ThreadMessage> messages = afterRunMessagesResponses.Value.Data;

// Messages iterate from newest to oldest, with the message[0] being the most recent
foreach (ThreadMessage threadMessage in messages)
{
    Console.WriteLine($"{threadMessage.CreatedAt:yyyy-MM-dd HH:mm:ss} - {threadMessage.Role,10}:");
    foreach (MessageContent contentItem in threadMessage.ContentItems)
    {
        if (contentItem is MessageTextContent textItem)
        {
            Console.WriteLine(textItem.Text);
        }
        else if (contentItem is MessageImageFileContent imageFileContent)
        {
            Console.WriteLine($"<image from ID: {imageFileContent.FileId}");
        }
        Console.WriteLine();
    }
}