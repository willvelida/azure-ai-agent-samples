## Basic Azure AI Foundry authentication with API Keys.

This sample deploys a basic Azure AI Agent Service using API Keys for authentication between the Azure AI Service and Azure OpenAI connection. Agents use multi-tenant search and storage resources that are managed by Microsoft.

## Deployment

To deploy this sample, use the AZ CLI to create the resource group:

```bash
az group create --name <rg-name> --location <location>
```

Then deploy the Bicep template to the resource group:

```bash
az deployment group create --resource-group rg-aihub-basic --template-file .\main.bicep --parameters .\main.parameters.json 
```