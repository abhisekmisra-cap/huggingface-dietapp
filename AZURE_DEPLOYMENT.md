# 🚀 Azure Web App Deployment Guide

This guide will help you deploy the Diet Plan Generator to Azure Web App.

## 📋 Prerequisites

1. **Azure Account**: Sign up at [portal.azure.com](https://portal.azure.com)
2. **Azure CLI**: Install from [docs.microsoft.com/cli/azure/install-azure-cli](https://docs.microsoft.com/cli/azure/install-azure-cli)
3. **Git**: For code deployment
4. **Hugging Face Account**: Get API token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

## 🔧 Step 1: Prepare Your Application

### 1.1 Files Created for Azure Deployment
- ✅ `startup.py` - Azure startup script
- ✅ `web.config` - IIS configuration
- ✅ `deploy.cmd` - Custom deployment script
- ✅ `.deployment` - Deployment configuration
- ✅ `azure_config.py` - Azure-specific settings
- ✅ `requirements.txt` - Python dependencies

### 1.2 Environment Variables Needed
- `HUGGINGFACE_API_TOKEN` - Your Hugging Face API token (required)
- `SECRET_KEY` - Flask secret key for sessions (recommended)
- `FLASK_DEBUG` - Set to 'False' for production

## 🌐 Step 2: Create Azure Web App

### 2.1 Using Azure Portal (GUI Method)

1. **Login to Azure Portal**
   - Go to [portal.azure.com](https://portal.azure.com)
   - Sign in with your Azure account

2. **Create Resource Group**
   - Click "Resource groups" → "Create"
   - Name: `diet-plan-rg`
   - Region: Choose closest to your users
   - Click "Review + create" → "Create"

3. **Create Web App**
   - Click "Create a resource" → "Web App"
   - **Basics:**
     - Subscription: Your subscription
     - Resource Group: `diet-plan-rg`
     - Name: `your-diet-plan-app` (must be globally unique)
     - Publish: `Code`
     - Runtime stack: `Python 3.11`
     - Operating System: `Linux`
     - Region: Same as resource group
   - **App Service Plan:**
     - Create new: `diet-plan-plan`
     - Pricing tier: `F1 (Free)` or `B1 (Basic)` for production
   - Click "Review + create" → "Create"

### 2.2 Using Azure CLI (Command Line Method)

```bash
# Login to Azure
az login

# Create resource group
az group create --name diet-plan-rg --location "East US"

# Create App Service plan
az appservice plan create --name diet-plan-plan --resource-group diet-plan-rg --sku F1 --is-linux

# Create Web App
az webapp create --resource-group diet-plan-rg --plan diet-plan-plan --name your-diet-plan-app --runtime "PYTHON|3.11"
```

## ⚙️ Step 3: Configure Environment Variables

### 3.1 Using Azure Portal
1. Go to your Web App → "Configuration" → "Application settings"
2. Add these variables:
   - `HUGGINGFACE_API_TOKEN`: Your API token
   - `SECRET_KEY`: Generate a secure random string
   - `FLASK_DEBUG`: `False`
   - `SCM_DO_BUILD_DURING_DEPLOYMENT`: `true`

### 3.2 Using Azure CLI
```bash
# Set environment variables
az webapp config appsettings set --resource-group diet-plan-rg --name your-diet-plan-app --settings \
    HUGGINGFACE_API_TOKEN="your_token_here" \
    SECRET_KEY="your_secret_key_here" \
    FLASK_DEBUG="False" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```

## 📦 Step 4: Deploy Your Application

### 4.1 Deploy from Local Git

1. **Initialize Git** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit for Azure deployment"
```

2. **Configure Azure Git Deployment**:
```bash
# Get deployment credentials
az webapp deployment source config-local-git --resource-group diet-plan-rg --name your-diet-plan-app

# Add Azure remote (replace with your actual URL)
git remote add azure https://your-diet-plan-app.scm.azurewebsites.net:443/your-diet-plan-app.git

# Deploy to Azure
git push azure main
```

### 4.2 Deploy from GitHub

1. **Fork/Upload to GitHub**:
   - Create a GitHub repository
   - Push your code to GitHub

2. **Configure GitHub Deployment**:
   - Azure Portal → Your Web App → "Deployment Center"
   - Source: "GitHub"
   - Authorize Azure to access GitHub
   - Select your repository and branch
   - Click "Save"

### 4.3 Deploy using VS Code

1. **Install Azure Extension**:
   - Install "Azure App Service" extension in VS Code

2. **Deploy**:
   - Right-click your project folder
   - Select "Deploy to Web App"
   - Choose your Azure subscription and Web App
   - Confirm deployment

## 🔍 Step 5: Verify Deployment

### 5.1 Check Application Status
1. **Azure Portal**:
   - Go to your Web App → "Overview"
   - Check if status is "Running"
   - Click on the URL to test your app

2. **Test Application**:
   - Navigate to `https://your-diet-plan-app.azurewebsites.net`
   - Fill out the diet plan form
   - Verify API token is working

### 5.2 Monitor Logs
```bash
# Stream logs
az webapp log tail --resource-group diet-plan-rg --name your-diet-plan-app

# Or in Azure Portal: Your Web App → "Log stream"
```

## 🐛 Troubleshooting

### Common Issues

1. **Application not starting**:
   - Check logs in Azure Portal → Log stream
   - Verify `startup.py` is correctly configured
   - Ensure all dependencies in `requirements.txt`

2. **Import errors**:
   - Check Python version compatibility
   - Verify all files are deployed
   - Check application settings

3. **API token issues**:
   - Verify `HUGGINGFACE_API_TOKEN` is set correctly
   - Test token with Hugging Face API directly

4. **CSRF token errors**:
   - Ensure `SECRET_KEY` is set
   - Check if HTTPS is properly configured

### Debug Commands
```bash
# Check app settings
az webapp config appsettings list --resource-group diet-plan-rg --name your-diet-plan-app

# Restart app
az webapp restart --resource-group diet-plan-rg --name your-diet-plan-app

# Check deployment status
az webapp deployment source show --resource-group diet-plan-rg --name your-diet-plan-app
```

## 🔒 Security Considerations

### Production Checklist
- ✅ Set `FLASK_DEBUG=False`
- ✅ Use strong `SECRET_KEY`
- ✅ Enable HTTPS (automatic in Azure)
- ✅ Keep `HUGGINGFACE_API_TOKEN` secure
- ✅ Monitor application logs
- ✅ Set up backup strategy

### Optional Security Enhancements
```bash
# Enable HTTPS only
az webapp update --resource-group diet-plan-rg --name your-diet-plan-app --https-only true

# Configure custom domain (optional)
az webapp config hostname add --resource-group diet-plan-rg --webapp-name your-diet-plan-app --hostname www.yourdomain.com
```

## 💰 Cost Management

### Free Tier Limits
- **F1 (Free)**: 1GB storage, 165MB/day bandwidth
- **Usage**: Perfect for development and testing
- **Limitations**: Custom domain not supported, limited compute

### Upgrade Options
- **B1 (Basic)**: $13-18/month, custom domain, SSL
- **P1 (Premium)**: $146/month, auto-scaling, backup

## 📊 Monitoring & Maintenance

### Application Insights (Recommended)
```bash
# Enable Application Insights
az monitor app-insights component create --app your-diet-plan-app --location "East US" --resource-group diet-plan-rg
```

### Regular Maintenance
- Monitor application logs
- Update dependencies regularly
- Backup application settings
- Monitor usage and costs

## 🎉 Success!

Your Diet Plan Generator is now live on Azure! 

**Your app URL**: `https://your-diet-plan-app.azurewebsites.net`

### Share Your App
- Send the URL to users
- Add custom domain if needed
- Monitor usage and feedback

---

**Developed by:** Dr. Abhishek Mishra  
**Powered by:** Hugging Face LLMs & Microsoft Azure  
**Purpose:** Experimentation & Learning