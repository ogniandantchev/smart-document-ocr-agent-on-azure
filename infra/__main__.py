"""
Pulumi infrastructure for Azure AI Agent with Mistral OCR
"""
import pulumi
import pulumi_azure_native as azure
from pulumi_azure_native import resources, machinelearningservices, cognitiveservices

# Configuration
config = pulumi.Config()
location = config.get("location") or "eastus"
project_name = config.get("projectName") or "ocr-agent-demo"

# Resource Group
resource_group = resources.ResourceGroup(
    f"{project_name}-rg",
    resource_group_name=f"{project_name}-rg",
    location=location,
    tags={
        "Environment": "Demo",
        "Project": "DocumentOCRAgent",
        "ManagedBy": "Pulumi"
    }
)

# Storage Account for AI Hub
storage_account = azure.storage.StorageAccount(
    f"{project_name}storage",
    account_name=f"{project_name.replace('-', '')}st",
    resource_group_name=resource_group.name,
    location=location,
    sku=azure.storage.SkuArgs(name="Standard_LRS"),
    kind="StorageV2",
    tags={"Purpose": "AIHub"}
)

# Key Vault for secrets
key_vault = azure.keyvault.Vault(
    f"{project_name}-kv",
    vault_name=f"{project_name}-kv",
    resource_group_name=resource_group.name,
    location=location,
    properties=azure.keyvault.VaultPropertiesArgs(
        tenant_id=config.require("tenantId"),
        sku=azure.keyvault.SkuArgs(
            family="A",
            name="standard"
        ),
        access_policies=[],
        enable_rbac_authorization=True
    ),
    tags={"Purpose": "AIHub"}
)

# Application Insights
app_insights = azure.insights.Component(
    f"{project_name}-insights",
    resource_name=f"{project_name}-insights",
    resource_group_name=resource_group.name,
    location=location,
    kind="web",
    application_type="web",
    tags={"Purpose": "Monitoring"}
)

# Azure AI Hub (Workspace)
ai_hub = machinelearningservices.Workspace(
    f"{project_name}-hub",
    workspace_name=f"{project_name}-hub",
    resource_group_name=resource_group.name,
    location=location,
    kind="Hub",
    sku=machinelearningservices.SkuArgs(
        name="Basic",
        tier="Basic"
    ),
    storage_account=storage_account.id,
    key_vault=key_vault.id,
    application_insights=app_insights.id,
    identity=machinelearningservices.ManagedServiceIdentityArgs(
        type="SystemAssigned"
    ),
    public_network_access="Enabled",
    tags={"Purpose": "AIFoundry"}
)

# Azure AI Project (Hub Connection)
ai_project = machinelearningservices.Workspace(
    f"{project_name}-project",
    workspace_name=f"{project_name}-project",
    resource_group_name=resource_group.name,
    location=location,
    kind="Project",
    hub_resource_id=ai_hub.id,
    identity=machinelearningservices.ManagedServiceIdentityArgs(
        type="SystemAssigned"
    ),
    public_network_access="Enabled",
    tags={"Purpose": "OCRAgent"}
)

# Azure AI Services (for model deployment)
ai_services = cognitiveservices.Account(
    f"{project_name}-aiservices",
    account_name=f"{project_name}-aiservices",
    resource_group_name=resource_group.name,
    location=location,
    kind="AIServices",
    sku=cognitiveservices.SkuArgs(name="S0"),
    properties=cognitiveservices.AccountPropertiesArgs(
        custom_sub_domain_name=f"{project_name}-aiservices",
        public_network_access="Enabled"
    ),
    tags={"Purpose": "ModelDeployment"}
)

# Outputs
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("ai_hub_name", ai_hub.name)
pulumi.export("ai_project_name", ai_project.name)
pulumi.export("ai_services_endpoint", ai_services.properties.endpoint)
pulumi.export("ai_services_name", ai_services.name)
pulumi.export("storage_account_name", storage_account.name)
pulumi.export("key_vault_name", key_vault.name)

# Instructions for next steps
pulumi.export("next_steps", pulumi.Output.concat(
    "1. Deploy Mistral OCR model from Azure AI Foundry catalog\n",
    "2. Get the model endpoint and key\n",
    "3. Update .env file with the values\n",
    "4. Run: pulumi stack output to see all resource names"
))