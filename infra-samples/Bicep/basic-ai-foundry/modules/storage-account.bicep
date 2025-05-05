@description('The name of the Application')
param applicationName string

@description('The environment that this storage account will be deployed to')
param environmentName string

@description('The Azure region that this storage account will be deployed to. Default is "eastus2"')
@allowed([
  'eastus'
  'eastus2'
  'swedencentral'
  'westus'
  'westus3'
])
param location string = 'eastus2'

@description('The SKU applied to this storage account. Default value is "Standard_LRS"')
@allowed([
  'Standard_LRS'
  'Standard_ZRS'
  'Standard_GRS'
  'Standard_GZRS'
  'Standard_RAGRS'
  'Standard_RAGZRS'
  'Premium_LRS'
  'Premium_ZRS'
])
param storageSku string = 'Standard_LRS'

@description('The tags that will be applied to this storage account')
param tags object = {}

resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: replace('${applicationName}${environmentName}stor','-','')
  location: location
  tags: tags
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    allowSharedKeyAccess: true
    encryption: {
      keySource: 'Microsoft.Storage'
      requireInfrastructureEncryption: false
      services: {
        blob: {
          enabled: true
          keyType: 'Account'
        }
        file: {
          enabled: true
          keyType: 'Account'
        }
        queue: {
          enabled: true
          keyType: 'Service'
        }
        table: {
          enabled: true
          keyType: 'Service'
        }
      }
    }
    isHnsEnabled: false
    isNfsV3Enabled: false
    keyPolicy: {
      keyExpirationPeriodInDays: 7
    }
    largeFileSharesState: 'Disabled'
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
    supportsHttpsTrafficOnly: true
  }
}

@description('The resource Id of the deployed Storage Account')
output storageId string = storage.id
