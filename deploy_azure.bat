@echo off
REM Azure Web App Deployment Script for Windows
REM Run this script to deploy your Diet Plan Generator to Azure

echo 🚀 Azure Web App Deployment Script
echo ==================================

REM Check if Azure CLI is installed
where az >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Azure CLI is not installed. Please install it first:
    echo    https://docs.microsoft.com/cli/azure/install-azure-cli
    pause
    exit /b 1
)

REM Configuration variables
set RESOURCE_GROUP=diet-plan-rg
set APP_SERVICE_PLAN=diet-plan-plan
set LOCATION=East US

echo 📝 Configuration Setup
echo ======================

REM Get Web App name from user
set /p WEBAPP_NAME="Enter your Web App name (must be globally unique): "
if "%WEBAPP_NAME%"=="" (
    echo ❌ Web App name cannot be empty
    pause
    exit /b 1
)

REM Get Hugging Face API token
set /p HF_TOKEN="Enter your Hugging Face API token: "
if "%HF_TOKEN%"=="" (
    echo ⚠️  Warning: No API token provided. App may not work properly.
)

REM Generate secret key (simplified for Windows)
set SECRET_KEY=change-this-secret-key-in-production-%RANDOM%-%RANDOM%

echo.
echo 🔐 Login to Azure
echo ==================
echo Checking Azure login status...
call az account show >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo You are not logged in to Azure. Logging in now...
    call az login
) else (
    echo You are already logged in to Azure.
)

echo.
echo 🔍 Verifying Azure Subscription
echo ================================
echo Current subscription:
call az account show --query "name" -o tsv
echo.
echo Available subscriptions:
call az account list --query "[].{Name:name, SubscriptionId:id, IsDefault:isDefault}" -o table
echo.
set /p CONFIRM_SUB="Do you want to use the current subscription? (y/n): "
if /i "%CONFIRM_SUB%" NEQ "y" (
    echo.
    echo Please set your desired subscription using:
    echo az account set --subscription "your-subscription-id"
    pause
    exit /b 1
)

echo.
echo 🏗️  Creating Azure Resources
echo ============================

REM Create resource group
echo Creating resource group: %RESOURCE_GROUP%
call az group create --name %RESOURCE_GROUP% --location "%LOCATION%"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to create resource group
    pause
    exit /b 1
)

REM Create App Service plan (Free tier)
echo Creating App Service plan: %APP_SERVICE_PLAN%
call az appservice plan create --name %APP_SERVICE_PLAN% --resource-group %RESOURCE_GROUP% --sku F1 --is-linux
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to create App Service plan
    pause
    exit /b 1
)

REM Create Web App
echo Creating Web App: %WEBAPP_NAME%
call az webapp create --resource-group %RESOURCE_GROUP% --plan %APP_SERVICE_PLAN% --name %WEBAPP_NAME% --runtime "PYTHON|3.11"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to create Web App
    pause
    exit /b 1
)

echo.
echo ⚙️  Configuring Environment Variables
echo ====================================

REM Set application settings
call az webapp config appsettings set --resource-group %RESOURCE_GROUP% --name %WEBAPP_NAME% --settings HUGGINGFACE_API_TOKEN="%HF_TOKEN%" SECRET_KEY="%SECRET_KEY%" FLASK_DEBUG="False" SCM_DO_BUILD_DURING_DEPLOYMENT="true"

echo.
echo 📦 Deploying Application
echo =======================

REM Initialize git if not already done
if not exist ".git" (
    echo Initializing Git repository
    git init
    git add .
    git commit -m "Initial commit for Azure deployment"
)

REM Configure local git deployment
echo Configuring Git deployment
for /f "delims=" %%i in ('az webapp deployment source config-local-git --resource-group %RESOURCE_GROUP% --name %WEBAPP_NAME% --query url -o tsv') do set DEPLOYMENT_URL=%%i

REM Add Azure remote
git remote remove azure 2>nul
git remote add azure %DEPLOYMENT_URL%

REM Deploy to Azure
echo Deploying to Azure (this may take a few minutes)...
git push azure main

echo.
echo ✅ Deployment Complete!
echo =======================
echo.
echo 🌐 Your app is available at:
echo    https://%WEBAPP_NAME%.azurewebsites.net
echo.
echo 📊 Monitor your app:
echo    Azure Portal: https://portal.azure.com
echo    Resource Group: %RESOURCE_GROUP%
echo    Web App: %WEBAPP_NAME%
echo.
echo 🔍 View logs:
echo    az webapp log tail --resource-group %RESOURCE_GROUP% --name %WEBAPP_NAME%
echo.
echo 🎉 Happy hosting!
pause