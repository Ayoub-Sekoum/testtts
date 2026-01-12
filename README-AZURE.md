# Azure Deployment Guide for Automattuner

This guide provides instructions for deploying the Automattuner web application to Microsoft Azure using the provided ARM template.

## Prerequisites

1.  **Azure CLI:** You must have the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and configured.
2.  **Docker:** Docker must be running on your local machine to build and push the container images.
3.  **GitHub Container Registry (GHCR):** You need to be authenticated with GHCR to push the Docker images.
4.  **jq:** A lightweight and flexible command-line JSON processor.

## Deployment Steps

### 1. Login to Azure

Open a terminal and login to your Azure account:

```bash
az login
```

Select the subscription you want to use:

```bash
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"
```

### 2. Create a Resource Group

Create a resource group in the desired location:

```bash
az group create --name "automattuner-rg" --location "westeurope"
```

### 3. Create a Key Vault and Store Secrets

The deployment requires a Key Vault to store sensitive information like the SQL administrator password.

```bash
# Create a unique Key Vault name
KEY_VAULT_NAME="automattuner-kv-$(openssl rand -hex 4)"

# Create the Key Vault
az keyvault create --name $KEY_VAULT_NAME --resource-group "automattuner-rg" --location "westeurope" --enable-rbac-authorization

# Store the SQL Admin Password (replace with a strong password)
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "sqlAdminPassword" --value "YOUR_STRONG_PASSWORD"

# Store the Azure AD App Registration secrets
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "AZURE-CLIENT-ID" --value "YOUR_AZURE_CLIENT_ID"
az keyvault secret set --vault-name $KEY_VAULT_NAME --name "AZURE-CLIENT-SECRET" --value "YOUR_AZURE_CLIENT_SECRET"
```

### 4. Build and Push Docker Images

Before deploying, you need to build the Docker images and push them to a container registry (e.g., GHCR).

```bash
# Login to GitHub Container Registry
docker login ghcr.io -u YOUR_GITHUB_USERNAME

# Build, tag, and push each image
docker-compose -f docker-compose-azure.yml build
docker-compose -f docker-compose-azure.yml push
```

*Note: Make sure the image names in `docker-compose-azure.yml` match your container registry repository.*

### 5. Update `parameters.json`

You need to update the `parameters.json` file with your Key Vault ID and the Base64 encoded Docker Compose file.

1.  **Get Key Vault ID:**
    ```bash
    KEY_VAULT_ID=$(az keyvault show --name $KEY_VAULT_NAME --resource-group "automattuner-rg" --query "id" -o tsv)
    ```

2.  **Update Key Vault reference in `parameters.json`:**
    *   Open `parameters.json` and replace the placeholder `id` in the `sqlAdminPassword` reference with the `$KEY_VAULT_ID` you just retrieved.

3.  **Encode `docker-compose-azure.yml`:**
    ```bash
    DOCKER_COMPOSE_BASE64=$(cat docker-compose-azure.yml | base64 | tr -d '\n')
    ```

4.  **Update `dockerComposeBase64` value:**
    *   Replace `"REPLACE_WITH_BASE64_ENCODED_DOCKER_COMPOSE"` in `parameters.json` with the value of the `$DOCKER_COMPOSE_BASE64` variable.

### 6. Deploy the ARM Template

Now, deploy the application using the ARM template and the updated parameters file.

```bash
az deployment group create \
    --resource-group "automattuner-rg" \
    --template-file "azuredeploy.json" \
    --parameters "@parameters.json" \
    --parameters sqlAdminLogin="sqladminuser" sqlAdminPassword="YOUR_STRONG_PASSWORD"
```

*Note: The deployment may take several minutes.*

## Post-Deployment

1.  **Get the Web App URL:**
    Once the deployment is complete, the output will include the URL of your web application.

2.  **Configure Redirect URI:**
    In your Azure AD App Registration, add the deployed Web App URL as a Redirect URI to enable authentication.

Your Automattuner web application is now deployed and ready to use.
