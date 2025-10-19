#!/bin/bash
# Azure Web App Deployment Script
# Run this script to deploy your Diet Plan Generator to Azure

echo "🚀 Azure Web App Deployment Script"
echo "=================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Configuration variables
RESOURCE_GROUP="diet-plan-rg"
APP_SERVICE_PLAN="diet-plan-plan"
WEBAPP_NAME=""
LOCATION="East US"

echo "📝 Configuration Setup"
echo "======================"

# Get Web App name from user
while [ -z "$WEBAPP_NAME" ]; do
    read -p "Enter your Web App name (must be globally unique): " WEBAPP_NAME
    if [ -z "$WEBAPP_NAME" ]; then
        echo "❌ Web App name cannot be empty"
    fi
done

# Get Hugging Face API token
read -p "Enter your Hugging Face API token: " HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  Warning: No API token provided. App may not work properly."
fi

# Generate secret key
SECRET_KEY=$(openssl rand -base64 32)

echo ""
echo "🔐 Login to Azure"
echo "=================="
az login

echo ""
echo "🏗️  Creating Azure Resources"
echo "============================"

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create App Service plan (Free tier)
echo "Creating App Service plan: $APP_SERVICE_PLAN"
az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku F1 --is-linux

# Create Web App
echo "Creating Web App: $WEBAPP_NAME"
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $WEBAPP_NAME --runtime "PYTHON|3.11"

echo ""
echo "⚙️  Configuring Environment Variables"
echo "===================================="

# Set application settings
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME --settings \
    HUGGINGFACE_API_TOKEN="$HF_TOKEN" \
    SECRET_KEY="$SECRET_KEY" \
    FLASK_DEBUG="False" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

echo ""
echo "📦 Deploying Application"
echo "======================="

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "Initializing Git repository"
    git init
    git add .
    git commit -m "Initial commit for Azure deployment"
fi

# Configure local git deployment
echo "Configuring Git deployment"
DEPLOYMENT_URL=$(az webapp deployment source config-local-git --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME --query url -o tsv)

# Add Azure remote
git remote remove azure 2>/dev/null || true
git remote add azure $DEPLOYMENT_URL

# Deploy to Azure
echo "Deploying to Azure (this may take a few minutes)..."
git push azure main

echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo ""
echo "🌐 Your app is available at:"
echo "   https://$WEBAPP_NAME.azurewebsites.net"
echo ""
echo "📊 Monitor your app:"
echo "   Azure Portal: https://portal.azure.com"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Web App: $WEBAPP_NAME"
echo ""
echo "🔍 View logs:"
echo "   az webapp log tail --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME"
echo ""
echo "🎉 Happy hosting!"