#!/bin/bash

# Azure App Service startup script for Plex Invite Application

echo "Starting Plex Invite Application..."

# Initialize database if needed
python -c "from app import create_app; from app.models import init_db; app = create_app(); app.app_context().push(); init_db(); print('Database initialized')"

# Start Gunicorn with recommended settings
gunicorn --bind=0.0.0.0:8000 \
         --workers=2 \
         --threads=4 \
         --timeout=120 \
         --access-logfile=- \
         --error-logfile=- \
         --log-level=info \
         "app:create_app()"

