@description('The name of the Application')
param applicationName string

@description('The environment that this Key Vault will be deployed to')
param environmentName string

@description('The Azure region that this Key Vault will be deployed to. Default is "eastus2"')
@allowed([
  'eastus'
  'eastus2'
  'swedencentral'
  'westus'
  'westus3'
])
param location string = 'eastus2'

@description('The tags that will be applied to the Key Vault')
param tags object

var keyVaultName = '${applicationName}-${environmentName}-kv'

resource keyVault 'Microsoft.KeyVault/vaults@2024-11-01' = {
  name: keyVaultName
  tags: tags
  location: location
  properties: {
    sku: {
      name: 'standard'
      family: 'A'
    }
    tenantId: subscription().tenantId
    enabledForTemplateDeployment: true
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

@description('The resource Id of the deployed Key Vault')
output keyVaultId string = keyVault.id
