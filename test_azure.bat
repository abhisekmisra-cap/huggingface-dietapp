@echo off
REM Azure Login and Subscription Test Script

echo 🔍 Azure CLI Diagnostics
echo =========================

echo 1. Checking Azure CLI version...
call az --version

echo.
echo 2. Checking login status...
call az account show
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Not logged in to Azure
    echo.
    echo Please run: az login
    pause
    exit /b 1
) else (
    echo ✅ Successfully logged in to Azure
)

echo.
echo 3. Listing available subscriptions...
call az account list --output table

echo.
echo 4. Checking current subscription...
call az account show --query "{Name:name, SubscriptionId:id, State:state}" --output table

echo.
echo 5. Testing resource group list (to verify permissions)...
call az group list --output table
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to list resource groups. Please check your subscription permissions.
    pause
    exit /b 1
) else (
    echo ✅ Successfully accessed Azure resources
)

echo.
echo 🎉 Azure CLI is properly configured!
echo You can now run deploy_azure.bat
pause