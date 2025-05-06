@description('The name of the Application')
param applicationName string

@description('The environment that this AI Services account will be deployed to')
param environmentName string

@description('The Azure region that this AI Services account will be deployed to. Default is "eastus2"')
@allowed([
  'eastus'
  'eastus2'
  'swedencentral'
  'westus'
  'westus3'
])
param location string = 'eastus2'

@description('The name of the model that we will deploy. Default is "gpt-4o-mini"')
param modelName string = 'gpt-4o-mini'

@description('The tags that will be applied to this AI Services account')
param tags object = {}

var aiServicesName = '${applicationName}-${environmentName}-aiservice'

resource aiServices 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: aiServicesName
  location: location
  tags: tags
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: toLower(aiServicesName)
    publicNetworkAccess: 'Enabled'
  }
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  name: modelName
  parent: aiServices
  sku: {
    name: 'GlobalStandard'
    capacity: 100
  }
  properties: {
    model: {
      name: modelName
      version: '2024-07-18'
      format: 'OpenAI'
    }
  }
}

@description('The resource Id of the deployed Azure AI Service')
output aiServiceId string = aiServices.id

@description('The name of the deployed AI Services account')
output aiServiceName string = aiServices.name

@description('The endpoint of the deployed AI Service')
output aiServiceEndpoint string = aiServices.properties.endpoint
