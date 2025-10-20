#!/usr/bin/env python3
"""
Main entry point for the Plex Invite Automation application.
"""

import os
from app import create_app
from app.models import init_db
from app.utils import setup_logging

# Setup logging
setup_logging()

# Create the Flask application
app = create_app()

# Initialize the database
with app.app_context():
    init_db()
    print("Database initialized successfully")

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Plex Invite System on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    # Run the application
    app.run(host=host, port=port, debug=debug)

