@echo off
REM Create Web App with Python 3.8
echo Creating Web App: abhi-diet-app
set RUNTIME=PYTHON^|3.8
az webapp create --resource-group diet-plan-rg --plan diet-plan-plan --name abhi-diet-app --runtime "%RUNTIME%"
echo Web App creation completed.