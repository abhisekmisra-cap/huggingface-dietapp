@echo off
REM Simple Azure Deployment Script for Diet Plan Generator

echo 🚀 Diet Plan Generator - Azure Deployment
echo ==========================================

REM Configuration
set RESOURCE_GROUP=diet-plan-rg
set APP_SERVICE_PLAN=diet-plan-plan
set LOCATION=eastus

echo.
echo 📝 Enter Deployment Details
echo ===========================

REM Get Web App name
set /p WEBAPP_NAME="Enter your Web App name (must be globally unique): "
if "%WEBAPP_NAME%"=="" (
    echo ❌ Web App name cannot be empty
    pause
    exit /b 1
)

REM Get API token
set /p HF_TOKEN="Enter your Hugging Face API token (optional): "

echo.
echo 🔍 Current Azure subscription:
call az account show --query "{Name:name, SubscriptionId:id}" --output table

echo.
set /p CONTINUE="Continue with deployment? (y/n): "
if /i "%CONTINUE%" NEQ "y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo 🏗️  Creating Resources
echo =====================

echo Step 1: Creating resource group...
call az group create --name %RESOURCE_GROUP% --location %LOCATION%
if %ERRORLEVEL% NEQ 0 goto :error

echo Step 2: Creating App Service plan...
call az appservice plan create --name %APP_SERVICE_PLAN% --resource-group %RESOURCE_GROUP% --sku F1 --is-linux
if %ERRORLEVEL% NEQ 0 goto :error

echo Step 3: Creating Web App...
set RUNTIME=PYTHON^|3.8
call az webapp create --resource-group %RESOURCE_GROUP% --plan %APP_SERVICE_PLAN% --name %WEBAPP_NAME% --runtime "%RUNTIME%"
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo ⚙️  Configuring App Settings
echo ============================
if not "%HF_TOKEN%"=="" (
    call az webapp config appsettings set --resource-group %RESOURCE_GROUP% --name %WEBAPP_NAME% --settings HUGGINGFACE_API_TOKEN="%HF_TOKEN%" SECRET_KEY="azure-secret-%RANDOM%" FLASK_DEBUG="False" SCM_DO_BUILD_DURING_DEPLOYMENT="true"
) else (
    call az webapp config appsettings set --resource-group %RESOURCE_GROUP% --name %WEBAPP_NAME% --settings SECRET_KEY="azure-secret-%RANDOM%" FLASK_DEBUG="False" SCM_DO_BUILD_DURING_DEPLOYMENT="true"
)
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo 📦 Setting up Git Deployment
echo =============================

REM Initialize git if needed
if not exist ".git" (
    echo Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit for Azure deployment"
)

REM Get deployment URL
echo Getting deployment URL...
for /f "delims=" %%i in ('az webapp deployment source config-local-git --resource-group %RESOURCE_GROUP% --name %WEBAPP_NAME% --query url -o tsv') do set DEPLOYMENT_URL=%%i

REM Configure git remote
git remote remove azure 2>nul
git remote add azure %DEPLOYMENT_URL%

echo.
echo 🚀 Deploying Application
echo =======================
echo This may take 5-10 minutes...
git push azure main
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo ✅ Deployment Successful!
echo =========================
echo.
echo 🌐 Your app is live at:
echo    https://%WEBAPP_NAME%.azurewebsites.net
echo.
echo 📊 Manage your app at:
echo    https://portal.azure.com
echo.
echo 🔍 View logs:
echo    az webapp log tail --resource-group %RESOURCE_GROUP% --name %WEBAPP_NAME%
echo.
echo 🎉 Congratulations! Your Diet Plan Generator is now hosted on Azure!
pause
exit /b 0

:error
echo.
echo ❌ Deployment failed!
echo ====================
echo Check the error messages above for details.
echo.
echo Common solutions:
echo 1. Make sure Web App name is globally unique
echo 2. Try a different Azure region if current one is full
echo 3. Check your Azure subscription permissions
echo.
pause
exit /b 1