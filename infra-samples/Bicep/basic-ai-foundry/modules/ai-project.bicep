@description('The name of the Application')
param applicationName string

@description('The environment that this AI Project account will be deployed to')
param environmentName string

@description('The Azure region that this AI Project account will be deployed to. Default is "eastus2"')
@allowed([
  'eastus'
  'eastus2'
  'swedencentral'
  'westus'
  'westus3'
])
param location string = 'eastus2'

@description('Resource ID of the AI Hub resource')
param aiHubId string

@description('The tags that will be applied to this AI Project account')
param tags object = {}

var projectName = '${applicationName}-${environmentName}-project'
var subscriptionId = subscription().subscriptionId
var resourceGroupName = resourceGroup().name
var projectConnectionString = '${location}.api.azureml.ms;${subscriptionId};${resourceGroupName};${projectName}'

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2025-01-01-preview' = {
  name: projectName
  tags: union(tags, {
    ProjectConnectionString: projectConnectionString
  })
  identity: {
    type: 'SystemAssigned'
  }
  location: location
  properties: {
    friendlyName: projectName
    description: 'This is a sample project.'
    hubResourceId: aiHubId
  }
  kind: 'Project'
}

@description('The resource Id of the deployed AI Project')
output aiProjectId string = aiProject.id

@description('The connection string of the deployed AI Project')
output aiProjectConnectionString string = aiProject.tags.ProjectConnectionString
