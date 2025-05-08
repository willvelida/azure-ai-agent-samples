using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.ChatCompletion;
using OpenAI;
using Plugins;
using SemanticKernelGitHubChatAgent;
using System.ClientModel;

Settings settings = new();

Console.WriteLine("Initializing plugins");
GitHubSettings gitHubSettings = settings.GetSettings<GitHubSettings>();
GitHubPlugin gitHubPlugin = new(gitHubSettings);
var modelId = "gpt-4.1";
var uri = "https://models.inference.ai.azure.com";

Console.WriteLine("Creating kernel");
IKernelBuilder builder = Kernel.CreateBuilder();

var client = new OpenAIClient(new ApiKeyCredential(gitHubSettings.Token), new OpenAIClientOptions
{
    Endpoint = new Uri(uri)
});

builder.AddOpenAIChatCompletion(modelId, client);

builder.Plugins.AddFromObject(gitHubPlugin);

Kernel kernel = builder.Build();

Console.WriteLine("Defining agent....");
ChatCompletionAgent chatCompletionAgent = new ChatCompletionAgent()
{
    Name = "SampleAssistantAgent",
    Instructions =
        """
        You are an agent designed to query and retrieve information from a single GitHub repository in a read-only manner.
        You are also able to access the profile of the active user.

        Use the current date and time to provide up-to-date details or time-sensitive responses.

        The repository you are querying is a public repository with the following name: {{$repository}}

        The current date and time is: {{$now}}. 
        """,
    Kernel = kernel,
    Arguments = new KernelArguments(new PromptExecutionSettings() { FunctionChoiceBehavior = FunctionChoiceBehavior.Auto() })
    {
        {
            "repository", "willvelida/azure-ai-agent-samples"
        }
    }
};

Console.WriteLine("Ready!");

ChatHistoryAgentThread agentThread = new ChatHistoryAgentThread();
bool isComplete = false;
do
{
    Console.WriteLine();
    Console.WriteLine("> ");
    string input = Console.ReadLine();
    if (string.IsNullOrWhiteSpace(input))
    {
        continue;
    }
    if (input.Trim().Equals("EXIT", StringComparison.OrdinalIgnoreCase))
    {
        isComplete = true;
        break;
    }

    var message = new ChatMessageContent(AuthorRole.User, input);

    Console.WriteLine();

    DateTime now = DateTime.Now;
    KernelArguments arguments = new KernelArguments()
    {
        {
            "now", $"{now.ToShortDateString()} {now.ToShortTimeString()}"
        }
    };

    await foreach (ChatMessageContent response in chatCompletionAgent.InvokeAsync(message, agentThread, options: new AgentInvokeOptions() { KernelArguments = arguments}))
    {
        Console.WriteLine($"{response.Content}");
    }
} while (!isComplete);
