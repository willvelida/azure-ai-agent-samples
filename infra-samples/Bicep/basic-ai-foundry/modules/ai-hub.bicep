@description('The name of the Application')
param applicationName string

@description('The environment that this AI Hub account will be deployed to')
param environmentName string

@description('The Azure region that this AI Hub account will be deployed to. Default is "eastus2"')
@allowed([
  'eastus'
  'eastus2'
  'swedencentral'
  'westus'
  'westus3'
])
param location string = 'eastus2'

@description('The tags that will be applied to this AI Hub account')
param tags object = {}

@description('Resource ID of the storage account resource for storing experimentation outputs')
param storageAccountId string

@description('Resource ID of the AI Services resource')
param aiServicesId string

@description('Resource ID of the AI Services endpoint')
param aiServicesTarget string

var aiHubName = '${applicationName}-${environmentName}-hub'

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2025-01-01-preview' = {
  name: aiHubName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: aiHubName
    description: 'This is a basic AI Foundry Hub'
    storageAccount: storageAccountId
  }
  kind: 'hub'

  resource aiServicesConnection 'connections@2025-01-01-preview' = {
    name: '${aiHubName}-connection-AIServices'
    properties: {
      category: 'AIServices'
      target: aiServicesTarget
      authType: 'ApiKey'
      isSharedToAll: true
      credentials: {
        key: '${listKeys(aiServicesId, '2022-10-01').key1}'
      }
      metadata: {
        ApiType: 'Azure'
        ResourceId: aiServicesId
        Location: location
      }
    }
  }
}

@description('The resource Id of the deployed AI Hub')
output aiHubId string = aiHub.id
