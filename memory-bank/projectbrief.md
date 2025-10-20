# Project Brief: Helpr - Plex Invite Automation System

## Overview
Helpr is a web application that automates the process of inviting friends and family to a Plex media server. The system provides a public-facing invite form and a secure admin dashboard for managing invitations and library access configuration.

## Core Objectives
1. **Automated Plex Invitations**: Allow users to request access via a web form and automatically receive Plex server invites
2. **Library Access Control**: Enable administrators to select which Plex libraries are shared with new users
3. **Secure Administration**: Provide a protected admin dashboard for monitoring invitations and configuring settings
4. **Mobile-Friendly**: Ensure the interface works seamlessly on all devices

## Key Features
- Public invite request form with optional invite code protection
- Automated Plex API integration for sending invitations
- Admin dashboard with:
  - Library selection and configuration
  - Invitation tracking and statistics
  - Plex connection testing
- Rate limiting to prevent abuse
- CSRF protection
- Secure password hashing
- Database tracking of all invitation requests

## Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite (development) / PostgreSQL (production/Azure)
- **Plex Integration**: PlexAPI library
- **Authentication**: Flask-Login
- **Security**: Flask-WTF (CSRF), Flask-Limiter (rate limiting)
- **Frontend**: Bootstrap 5, responsive design

## Deployment Context
- Development: Local SQLite database
- Production: Azure Web App with PostgreSQL
- WSGI: Gunicorn for production serving

## Success Criteria
1. Users can successfully request and receive Plex invitations without manual admin intervention
2. Admins can configure which libraries to share from a web dashboard
3. The system prevents abuse through rate limiting and optional invite codes
4. All invitation requests are tracked in the database
5. The application performs efficiently with minimal latency

## Current Status
- Core functionality implemented and working
- Deployed to Azure with PostgreSQL backend
- ✅ **PERFORMANCE OPTIMIZED**: Critical performance issues resolved (2025-10-20)
  - Eliminated redundant Plex API connections
  - Removed duplicate dashboard API calls
  - Reduced database query overhead

