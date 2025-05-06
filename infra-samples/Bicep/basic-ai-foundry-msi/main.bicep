@description('The name of the Application')
param applicationName string

@description('The environment that this application will be deployed to')
param environmentName string

@description('The tags that will be applied to all resources')
param tags object

module keyVault 'modules/key-vault.bicep' = {
  name: 'kv'
  params: {
    tags: tags
    applicationName: applicationName
    environmentName: environmentName
  }
}

module storageAccount 'modules/storage-account.bicep' = {
  name: 'storage'
  params: {
    applicationName: applicationName
    environmentName: environmentName
    tags: tags
  }
}

module aiServices 'modules/ai-services.bicep' = {
  name: 'aiServices'
  params: {
    applicationName: applicationName 
    environmentName: environmentName
    tags: tags
  }
}

module aiHub 'modules/ai-hub.bicep' = {
  name: 'aiHub'
  params: {
    aiServicesId: aiServices.outputs.aiServiceId
    aiServicesTarget: aiServices.outputs.aiServiceEndpoint
    applicationName: applicationName
    environmentName: environmentName
    storageAccountId: storageAccount.outputs.storageId
    tags: tags
  }
}

module aiProject 'modules/ai-project.bicep' = {
  name: 'aiProject'
  params: {
    aiHubId: aiHub.outputs.aiHubId
    applicationName: applicationName 
    environmentName: environmentName
    tags: tags
  }
}

module roleAssignments 'modules/ai-service-role-assignments.bicep' = {
  params: {
    aiProjectId: aiProject.outputs.aiProjectId
    aiProjectPrincipalId: aiProject.outputs.aiProjectPrincipalId
    aiServicesName: aiServices.outputs.aiServiceName
  }
}
