# Technical Context

## Technology Stack

### Backend Framework
- **Flask 3.0.x**: Lightweight Python web framework
- **Gunicorn 21.2.x**: WSGI production server

### Database
- **SQLAlchemy 2.0.x**: ORM for database interactions
- **Flask-SQLAlchemy 3.1.x**: Flask integration for SQLAlchemy
- **SQLite**: Development database
- **PostgreSQL** (psycopg2-binary): Production database on Azure

### Plex Integration
- **PlexAPI 4.15.x**: Official Python library for Plex Media Server API
- Handles authentication, server connection, library queries, and invitation sending

### Security & Authentication
- **Flask-Login 0.6.x**: User session management for admin
- **Flask-WTF 1.2.x**: CSRF protection and form handling
- **Werkzeug**: Password hashing (built into Flask)
- **Flask-Limiter 3.5.x**: Rate limiting for abuse prevention

### Environment & Configuration
- **python-dotenv 1.0.x**: Environment variable management from `.env` file
- `config.json`: Runtime configuration storage

### Python Version
- **Python 3.8+** required

## Project Structure

```
helpr/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── plex_service.py       # Plex API integration
│   ├── utils.py              # Utility functions
│   ├── routes/
│   │   ├── main.py           # Public routes
│   │   └── admin.py          # Admin routes
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── success.html
│   │   ├── 404.html
│   │   ├── 500.html
│   │   ├── setup_required.html
│   │   └── admin/
│   │       ├── login.html
│   │       └── dashboard.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
├── memory-bank/              # Project memory (NEW)
├── config.py                 # Configuration class
├── run.py                    # Development entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── env.template              # Environment template
├── config.json               # Library configuration
├── invites.db                # SQLite database (development)
├── Dockerfile                # Container definition
├── startup.sh                # Azure startup script
├── README.md                 # User documentation
├── prd.md                    # Product requirements
└── AZURE_DEPLOYMENT.md       # Deployment guide
```

## Development Setup

### Required Environment Variables
```
SECRET_KEY                  # Flask session encryption key
PLEX_TOKEN                  # Plex authentication token
PLEX_SERVER_NAME            # Name of Plex server to manage
ADMIN_USERNAME              # Admin login username
ADMIN_PASSWORD_HASH         # Hashed admin password
INVITE_CODE                 # Optional invite code (empty = open access)
DATABASE_PATH               # SQLite file path (dev only)
```

### Azure Production Variables
```
DATABASE_URL                # PostgreSQL connection string
AZURE_POSTGRESQL_CONNECTIONSTRING  # Alternative connection string format
WEBSITES_PORT               # Azure port configuration
```

## Database Schema

### InviteRequest Table
```sql
CREATE TABLE invite_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_or_username VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,  -- 'success' or 'failed'
    error_message TEXT
);
```

## Plex API Integration

### Authentication
- Uses X-Plex-Token for API authentication
- Token obtained from user's Plex account settings
- Token stored in environment variable

### Key API Operations
1. **Account Connection**: `MyPlexAccount(token=PLEX_TOKEN)`
2. **Server Discovery**: `account.resource(SERVER_NAME).connect()`
3. **Library Query**: `server.library.sections()`
4. **Send Invite**: `account.inviteFriend(user, server, sections)`

### API Endpoints Used (via PlexAPI)
- `https://plex.tv/api/v2/user` - Account verification
- `https://plex.tv/api/resources` - Server discovery
- `https://plex.tv/api/servers/{id}/shared_servers` - Invite creation

## Deployment Architecture

### Development
- Flask development server via `run.py`
- SQLite database
- Debug mode enabled
- Hot reload on code changes

### Production (Azure Web App)
- Gunicorn WSGI server (4 workers recommended)
- PostgreSQL database (Azure Database for PostgreSQL)
- HTTPS via Azure App Service
- Environment variables configured in Azure Portal
- Startup script: `startup.sh`

### Docker Support
- `Dockerfile` provided for containerization
- Can be deployed to Azure Container Instances or App Service

## Constraints & Limitations

### Technical Constraints
- Plex API rate limiting (not documented but exists)
- Plex limit of 100 shared users per server
- PlexAPI library requires stable network connection
- Database connection pool limits (SQLAlchemy)

### Security Constraints
- Plex token must be kept secret (like a password)
- HTTPS required for production (sensitive data)
- CSRF tokens must be validated on all forms
- Rate limiting required to prevent abuse

### Performance Constraints
- Plex API connections can be expensive (1-3 seconds) - **OPTIMIZED 2025-10-20**
  - ✅ Connection reuse implemented to minimize reconnections
  - ✅ Duplicate API calls eliminated from dashboard
- Network latency to Plex servers affects response times (inherent)
- Database queries optimized (reduced from 50 to 20 records per dashboard load)

## Known Issues
None - All critical issues resolved ✅

### Resolved Issues
1. **Performance**: Application was performing very slowly (RESOLVED 2025-10-20)
   - Root cause: Redundant Plex API connections
   - Solution: Implemented `_ensure_connected()` pattern and removed duplicate API calls
   - See `systemPatterns.md` and `activeContext.md` for implementation details

## Development Commands

### Run Locally
```bash
python run.py
```

### Run with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Generate Password Hash
```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('password'))"
```

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

