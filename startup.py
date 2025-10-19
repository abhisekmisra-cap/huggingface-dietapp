"""
Startup script for Azure Web App deployment
This file is used by Azure to start the Flask application
"""
import os
from app import app

if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    # Run the Flask app
    # Note: For production, Azure should use gunicorn via startup command
    app.run(
        host='0.0.0.0',  # Listen on all interfaces for Azure
        port=port,
        debug=False  # Disable debug mode in production
    )