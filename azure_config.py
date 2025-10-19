"""
Azure Web App Configuration
Environment variables and settings for Azure deployment
"""
import os

# Azure Web App environment variables
AZURE_CONFIG = {
    # Required environment variables for Azure
    'HUGGINGFACE_API_TOKEN': os.environ.get('HUGGINGFACE_API_TOKEN'),
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'change-this-secret-key-in-production'),
    'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'False'),
    'PORT': int(os.environ.get('PORT', 8000)),
    
    # Azure-specific settings
    'WEBSITE_HOSTNAME': os.environ.get('WEBSITE_HOSTNAME'),
    'WEBSITE_SITE_NAME': os.environ.get('WEBSITE_SITE_NAME'),
    
    # Application settings
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file size
    'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour session timeout
}

def get_azure_config():
    """Get Azure configuration dictionary"""
    return AZURE_CONFIG

def is_azure_environment():
    """Check if running in Azure Web App environment"""
    return os.environ.get('WEBSITE_SITE_NAME') is not None