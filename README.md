# Plex Invite Automation System

A web application that automates the process of inviting friends and family to your Plex server. Users can request access through a simple web form, and administrators can manage invitations and configure library access through a secure dashboard.

## Features

- **Public Invite Form**: Clean, mobile-friendly interface for users to request Plex access
- **Automated Invitations**: Automatically send Plex invitations via the PlexAPI
- **Admin Dashboard**: Secure dashboard for managing invitations and library settings
- **Library Configuration**: Select which Plex libraries to share with new users
- **Invite Tracking**: Track all invitation requests with timestamps and status
- **Optional Invite Codes**: Optionally require an invite code to restrict access
- **Rate Limiting**: Built-in rate limiting on invite requests (5/minute, 20/hour)
- **CSRF Protection**: Cross-Site Request Forgery protection on all forms
- **Secure Password Storage**: Admin passwords stored using industry-standard hashing
- **Mobile Responsive**: Fully responsive design that works on all devices

## Requirements

- Python 3.8 or higher
- Plex Media Server with Plex Pass (required for managed users)
- Plex authentication token
- Modern web browser

## Installation

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd plex-invite-automation
```

### 2. Create a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file by copying the example:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Flask Configuration
SECRET_KEY=your_secret_key_here

# Plex Configuration
PLEX_TOKEN=your_plex_token_here
PLEX_SERVER_NAME=your_plex_server_name

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_hashed_password_here

# Optional Invite Code (leave empty for open access)
INVITE_CODE=

# Database Configuration
DATABASE_PATH=invites.db

# Flask Server Configuration (Optional)
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

#### How to Get Your Plex Token

1. Sign in to your Plex account at https://app.plex.tv
2. Open any media item
3. Click the three dots menu (⋯) and select "Get Info"
4. Click "View XML"
5. Look for `X-Plex-Token` in the URL

Or follow the official guide: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

#### How to Generate a Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### How to Generate a Password Hash

For security, admin passwords are stored as hashes. Generate your password hash:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"
```

Copy the output and use it as your `ADMIN_PASSWORD_HASH` value.

### 5. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

### For Users (Requesting Access)

1. Navigate to the application URL
2. Enter your Plex username or email address
3. If required, enter the invite code provided by the administrator
4. Click "Request Invite"
5. Check your email for the Plex invitation
6. Accept the invitation to gain access to the shared libraries

### For Administrators

1. Navigate to `http://localhost:5000/admin/login`
2. Log in with your admin credentials
3. View the dashboard to see:
   - Plex connection status
   - Invitation statistics
   - Recent invitation requests
4. Configure which libraries to share:
   - Check the boxes next to libraries you want to share
   - Click "Save Library Settings"
5. Test the Plex connection using the "Test Connection" button

## Configuration

### Library Settings

Libraries to share are configured through the admin dashboard. The selected libraries are saved to `config.json` and will be shared with all new users who request access.

### Invite Code (Optional)

To restrict access to the invite form:

1. Set `INVITE_CODE` in your `.env` file
2. Share this code with trusted users
3. Users must enter the correct code to submit invite requests

### Database

The application uses SQLite to track invitation requests. The database file location is specified by `DATABASE_PATH` in the `.env` file.

## Security Considerations

### For Development

- The application runs in debug mode by default when using `run.py`
- Default credentials should be changed immediately
- Never commit your `.env` file to version control

### For Production Deployment

1. **Use HTTPS**: Always run behind a reverse proxy (nginx, Apache) with SSL/TLS
2. **Strong Credentials**: Use strong, unique passwords for admin access (stored as hashes)
3. **Secret Key**: Use a cryptographically secure random secret key
4. **WSGI Server**: Use a production WSGI server (Gunicorn, uWSGI) instead of Flask's development server
5. **Firewall**: Restrict access to necessary ports only
6. **Rate Limiting**: Built-in rate limiting (5 requests/minute, 20/hour on invite endpoint; 200/day, 50/hour globally)
7. **Updates**: Keep dependencies updated regularly
8. **CSRF Protection**: Enabled by default on all forms

### Example Production Setup with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Example Nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### "Invalid Plex token" Error

- Verify your Plex token is correct
- Ensure you have an active Plex Pass subscription
- Try regenerating your Plex token

### "Plex server not found" Error

- Check that `PLEX_SERVER_NAME` matches your server name exactly (case-sensitive)
- Ensure your Plex server is running and accessible
- Verify you're using the correct Plex account

### "User already has access" Error

- The user has already been invited or has existing access
- Check the Plex server's user management to verify

### Connection Issues

- Ensure your Plex server is accessible from the machine running the application
- Check firewall settings
- Verify network connectivity

### Email Not Received

- Check spam/junk folders
- Verify the email address is correct and associated with a Plex account
- Plex emails may take a few minutes to arrive

## Project Structure

```
plex-invite-automation/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── plex_service.py      # Plex API integration
│   ├── utils.py             # Utility functions
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py          # Public routes
│   │   └── admin.py         # Admin routes
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── success.html
│   │   ├── 404.html
│   │   ├── 500.html
│   │   └── admin/
│   │       ├── login.html
│   │       └── dashboard.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
├── config.py                # Configuration management
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore rules
├── config.json             # Library configuration
└── README.md               # This file
```

## Future Enhancements

Based on the project requirements document (PRD), potential future enhancements include:

- **Unique Invite Links**: Generate unique, single-use invitation links with expiration dates
- **Tiered Access Levels**: Different library access levels (basic, premium, etc.)
- **Email Notifications**: Send confirmation emails directly from the application
- **User Management**: View and revoke access for existing users
- **Advanced Statistics**: Detailed analytics and reporting
- **Webhook Integration**: Notify external services when invites are sent
- **Multi-language Support**: Internationalization for the user interface
- **OAuth Authentication**: Allow users to authenticate directly with Plex
- **Batch Invitations**: Upload CSV files to invite multiple users at once

## License

This project is provided as-is for personal use. Please ensure you comply with Plex's Terms of Service when using this application.

## Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review the project's issue tracker (if available)
3. Consult the Plex API documentation: https://python-plexapi.readthedocs.io/

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Plex integration via [Python-PlexAPI](https://python-plexapi.readthedocs.io/)
- UI styled with [Bootstrap 5](https://getbootstrap.com/)

