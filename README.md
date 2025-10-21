# Helpr - Plex Subscription Management Platform

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![Stripe](https://img.shields.io/badge/stripe-integrated-blueviolet.svg)

A complete subscription management platform for Plex servers with Stripe payment integration, tiered access levels, automatic expiry handling, and grandfathering support. Transform your Plex server into a managed service with recurring billing, automated access control, and comprehensive admin tools.

## ⚡ Quick Start

1. Clone the repository
2. Copy `env.template` to `.env` and configure your Plex credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python run.py`
5. Access admin dashboard at `http://localhost:5000/admin/login`

See [Installation](#installation) for detailed instructions.

## Features

### 💳 Subscription Management
- **Stripe Integration**: Full payment processing with recurring monthly subscriptions
- **Tiered Access**: Multiple subscription tiers with different features and pricing
- **Automatic Billing**: Stripe handles all payment processing and billing
- **Expiry Automation**: Automatic Plex access revocation when subscriptions expire
- **Grandfathering**: Migrate existing users to lifetime access
- **Free Tier**: Special invite codes for complimentary access

### 🎭 Access Control
- **Download Permissions**: Control sync/download capabilities per tier
- **Library Management**: Configure which libraries each tier can access
- **Automatic Invites**: Send Plex invitations immediately after successful payment
- **Access Revocation**: Automatically remove access on cancellation or expiry
- **Manual Controls**: Admin can manually extend or revoke subscriptions

### 📊 Admin Dashboard
- **Subscription Tracking**: View all active, expired, and cancelled subscriptions
- **Revenue Analytics**: Track Monthly Recurring Revenue (MRR) and subscription stats
- **Tier Management**: Create and configure subscription tiers with pricing
- **User Search**: Find subscriptions by email or Plex username
- **Stripe Portal**: Direct links to Stripe billing portal for customer management

### 🔒 Security & Performance
- **Webhook Verification**: Cryptographic verification of Stripe webhooks
- **CSRF Protection**: Cross-Site Request Forgery protection on all forms
- **Rate Limiting**: Built-in rate limiting (5/min on invite, 10/hour on checkout)
- **Secure Storage**: Industry-standard password hashing and secret management
- **Background Jobs**: APScheduler for automated expiry checking and cleanup

### 🎨 User Experience
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Clear Pricing**: Professional pricing cards showing tier features
- **Instant Access**: Automated invite delivery after successful payment
- **Email Notifications**: Stripe handles billing reminders and receipts
- **Success Pages**: Clear confirmation of subscription activation

## Requirements

- Python 3.8 or higher
- Plex Media Server with Plex Pass (required for managed users)
- Plex authentication token
- **Stripe Account** (for payment processing)
- Modern web browser
- PostgreSQL (production) or SQLite (development)

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/YOUR-USERNAME/helpr.git
cd helpr
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
cp env.template .env
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

### 8. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

### For Users (Subscribing)

1. Navigate to the application URL (redirects to `/plans`)
2. Choose a subscription tier (With Downloads or Without Downloads)
3. Enter your email address and optionally your Plex username
4. Click "Subscribe Now"
5. Complete payment on Stripe's secure checkout page
6. Check your email for:
   - Stripe payment confirmation
   - Plex invitation email
7. Accept the Plex invitation to gain access

**Free Access**: If you have a special invite code:
1. Scroll to "Have an Invite Code?" section
2. Enter your email/username and the code
3. Get instant access without payment

### For Administrators

#### Dashboard Overview
1. Navigate to `http://localhost:5000/admin/login`
2. Log in with your admin credentials
3. View the dashboard to see:
   - Plex connection status
   - Subscription statistics (active, MRR, grandfathered)
   - Recent invitation requests
   - Quick links to subscription and tier management

#### Subscription Management
1. Click "Manage Subscriptions" or go to `/admin/subscriptions`
2. View all subscriptions with filtering:
   - Filter by status (active, past_due, cancelled, expired)
   - Search by email or username
3. Click "View" on any subscription to:
   - See detailed subscription information
   - Link to Stripe billing portal
   - Manually revoke access
   - Extend subscription period

#### Tier Configuration
1. Go to `/admin/tiers`
2. Create new tiers with:
   - Name and description
   - Monthly price
   - Stripe Price ID
   - Download permissions (on/off)
   - Library access selection
3. Update or deactivate existing tiers
4. Libraries are assigned per-tier for granular control

#### Grandfather Existing Users
1. Go to `/admin/subscriptions`
2. Click "Grandfather Existing Users"
3. All users with successful invites become lifetime subscribers
4. They appear with "Grandfathered" badge

#### Library Settings
Configure default libraries (legacy mode):
1. Check boxes next to libraries to share
2. Click "Save Library Settings"
3. Note: Tier-based libraries override these defaults

## Configuration

### Subscription Tiers

Subscription tiers are the core of the platform. Each tier defines:

- **Pricing**: Monthly recurring price charged via Stripe
- **Libraries**: Which Plex libraries subscribers can access
- **Downloads**: Whether sync/download is enabled (allowSync in Plex)
- **Stripe Price ID**: Links to Stripe product pricing

Configure tiers at `/admin/tiers`.

### Free Tier Access

Grant complimentary access without payment:

1. Set `FREE_TIER_INVITE_CODE` in `.env`
2. Share this code with select users
3. They enter it on the plans page to get free access
4. Creates a grandfathered subscription (no expiry, no Stripe)

### Grandfathering

Migrate existing users to permanent access:

1. Use the "Grandfather Existing Users" button in `/admin/subscriptions`
2. All successful historic invites become lifetime subscriptions
3. Grandfathered users:
   - Show "Grandfathered" badge
   - No expiry date
   - No Stripe billing
   - Permanent access

### Library Settings (Legacy)

Default libraries can still be configured via the admin dashboard:
- Saved to `config.json`
- Used for free tier invites
- Overridden by tier-specific library settings

### Database

- **Development**: SQLite (DATABASE_PATH in `.env`)
- **Production**: PostgreSQL (DATABASE_URL or AZURE_POSTGRESQL_CONNECTIONSTRING)
- **Tables**: invite_requests, tiers, subscriptions
- **Migrations**: Automatic on startup via SQLAlchemy

## Security Considerations

### For Development

- The application runs in debug mode by default when using `run.py`
- Use Stripe test mode keys (pk_test_ and sk_test_)
- Test webhooks locally with Stripe CLI: `stripe listen --forward-to localhost:5000/webhook/stripe`
- Never commit your `.env` file to version control

### For Production Deployment

1. **Use HTTPS**: **REQUIRED** - Stripe webhooks only work over HTTPS
2. **Stripe Live Keys**: Switch from test to live keys in production
3. **Webhook Endpoint**: Configure in Stripe Dashboard pointing to your domain
4. **Strong Credentials**: Use strong, unique passwords for admin access (stored as hashes)
5. **Secret Key**: Use a cryptographically secure random secret key
6. **WSGI Server**: Use a production WSGI server (Gunicorn, uWSGI)
7. **Firewall**: Restrict access to necessary ports only
8. **Rate Limiting**: Built-in rate limiting:
   - 5/minute on invite requests
   - 10/hour on checkout
   - 200/day, 50/hour globally
9. **Updates**: Keep dependencies updated regularly
10. **CSRF Protection**: Enabled on all forms (webhooks exempt)
11. **Webhook Verification**: Always validates Stripe signatures
12. **Secrets Management**: Never expose Stripe secret keys in logs or errors

### Stripe Security Best Practices

1. **Never share** secret keys (sk_test_ or sk_live_)
2. **Rotate keys** immediately if compromised
3. **Verify webhook signatures** (handled automatically)
4. **Use HTTPS only** for production
5. **Monitor** Stripe Dashboard for unusual activity
6. **Test mode first** before going live
7. **Webhook URL** must be publicly accessible and secure

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

### Plex Issues

**"Invalid Plex token" Error**
- Verify your Plex token is correct
- Ensure you have an active Plex Pass subscription
- Try regenerating your Plex token

**"Plex server not found" Error**
- Check that `PLEX_SERVER_NAME` matches your server name exactly (case-sensitive)
- Ensure your Plex server is running and accessible
- Verify you're using the correct Plex account

**"User already has access" Error**
- The user has already been invited or has existing access
- Check the Plex server's user management to verify
- For existing users, use tier management to update permissions

**Email Not Received**
- Check spam/junk folders
- Verify the email address is correct and associated with a Plex account
- Plex emails may take a few minutes to arrive

### Stripe Issues

**Webhook Not Receiving Events**
1. Verify webhook URL in Stripe Dashboard is correct
2. Ensure URL is publicly accessible (not localhost in production)
3. Check webhook signing secret matches `.env`
4. Review webhook logs in Stripe Dashboard
5. For local testing, use Stripe CLI: `stripe listen --forward-to localhost:5000/webhook/stripe`

**Payment Successful but No Plex Invite**
1. Check application logs for errors during webhook processing
2. Verify tier has Stripe Price ID configured
3. Check subscription was created in `/admin/subscriptions`
4. Manually send invite from subscription detail page if needed

**Checkout Session Creation Fails**
1. Verify Stripe keys are correct (test vs live)
2. Check tier has valid Stripe Price ID
3. Ensure Price ID is for recurring (not one-time) payment
4. Review Stripe Dashboard for product/price status

**Subscription Not Cancelling**
1. Check Stripe webhook events are being received
2. Verify `customer.subscription.deleted` event is configured
3. Manual revoke available in admin panel as fallback

### General Issues

**Background Jobs Not Running**
- APScheduler runs in-process with the app
- Check application logs for scheduler initialization
- For multi-worker deployments, ensure only one worker runs scheduler

**Database Errors**
- SQLite for development should work automatically
- PostgreSQL requires proper DATABASE_URL configuration
- Check database connection string format for Azure

**Access Not Revoked on Expiry**
- Background job runs daily at midnight
- Check application logs for job execution
- Manually revoke via admin panel if needed
- Verify Plex credentials allow friend management

**MRR Not Calculating**
- Only active, non-grandfathered subscriptions count toward MRR
- Refresh dashboard to see updated statistics
- Check tier pricing is set correctly

## Project Structure

```
helpr/
├── app/
│   ├── __init__.py              # Application factory with scheduler
│   ├── models.py                # Database models (Tier, Subscription, InviteRequest)
│   ├── plex_service.py          # Plex API integration with revocation
│   ├── stripe_service.py        # Stripe payment processing (NEW)
│   ├── scheduler.py             # Background jobs for expiry (NEW)
│   ├── utils.py                 # Utility functions
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py              # Public routes + subscriptions
│   │   └── admin.py             # Admin routes + tier/subscription mgmt
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── success.html
│   │   ├── plans.html           # Subscription tier selection (NEW)
│   │   ├── subscription_success.html  # Post-payment page (NEW)
│   │   ├── 404.html
│   │   ├── 500.html
│   │   └── admin/
│   │       ├── login.html
│   │       ├── dashboard.html   # Updated with subscription stats
│   │       ├── subscriptions.html      # Subscription list (NEW)
│   │       ├── subscription_detail.html # Individual subscription (NEW)
│   │       └── tiers.html       # Tier management (NEW)
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
├── memory-bank/                 # Project documentation
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md
│   ├── progress.md
│   └── tasks.md
├── config.py                    # Configuration management with Stripe
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies (+ stripe, APScheduler)
├── env.template                 # Example environment variables
├── .cursorrules                 # Project intelligence
├── .gitignore                   # Git ignore rules
├── config.json                  # Library & tier configuration
├── invites.db                   # SQLite database (development)
├── README.md                    # This file
├── STRIPE_SETUP.md              # Stripe configuration guide (NEW)
├── SUBSCRIPTION_IMPLEMENTATION.md  # Technical implementation docs (NEW)
├── DEPLOYMENT.md                # Deployment guide
├── SECURITY.md                  # Security policy
└── LICENSE                      # GPL-3.0 license
```

## Implemented Features ✅

- ✅ **Tiered Subscriptions**: Multiple tiers with different pricing and features
- ✅ **Stripe Integration**: Full payment processing with webhooks
- ✅ **Automatic Expiry**: Background jobs revoke access on expiry
- ✅ **Grandfathering**: Migrate existing users to lifetime access
- ✅ **Download Control**: Per-tier sync/download permissions
- ✅ **Admin Management**: Complete subscription and tier management UI
- ✅ **Revenue Tracking**: MRR and subscription analytics

## Future Enhancements

Potential enhancements based on user feedback:

- **Trial Periods**: 7/14/30 day free trials before charging
- **Annual Billing**: Discounted yearly subscription option
- **Tier Changes**: Automatic tier upgrades/downgrades with proration
- **Usage Analytics**: Track which libraries users access most
- **Discount Codes**: Coupon system for promotions
- **Referral System**: Reward users for referring friends
- **Multi-Currency**: Support for EUR, GBP, CAD, etc.
- **Email Notifications**: Custom email templates for expiry warnings
- **Batch Management**: Bulk subscription operations
- **Advanced Reporting**: Export subscription data to CSV/Excel
- **Webhook Integration**: Notify Discord/Slack on new subscriptions
- **OAuth Authentication**: Allow users to sign in with Plex
- **Usage-Based Billing**: Charge based on concurrent streams
- **Family Plans**: Multi-user subscriptions

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Reporting bugs
- Suggesting features
- Submitting pull requests
- Development setup
- Code style guidelines

## Security

Found a security vulnerability? Please report it privately. See [SECURITY.md](SECURITY.md) for details on:

- How to report vulnerabilities
- Security best practices
- Supported versions

## Deployment

### Quick Deploy

For production deployment instructions, see:

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - General deployment guide (Docker, reverse proxy, cloud platforms)
- **[STRIPE_SETUP.md](STRIPE_SETUP.md)** - Stripe-specific configuration
- **[SUBSCRIPTION_IMPLEMENTATION.md](SUBSCRIPTION_IMPLEMENTATION.md)** - Technical architecture details

### Critical Production Steps

1. **Use HTTPS** - Required for Stripe webhooks
2. **Live Stripe Keys** - Switch from test to live mode
3. **Configure Webhook** - Set up endpoint in Stripe Dashboard
4. **PostgreSQL** - Use managed database for production
5. **Background Scheduler** - Ensure APScheduler runs (consider separate worker)
6. **Environment Variables** - Set all required vars in production environment
7. **Test Thoroughly** - Test complete subscription flow in test mode first

### Deployment Checklist

- [ ] HTTPS configured and working
- [ ] Stripe account in live mode
- [ ] Products and prices created in Stripe
- [ ] Webhook endpoint configured
- [ ] All environment variables set
- [ ] Database migrations run
- [ ] Tiers created in admin panel
- [ ] Test subscription flow works
- [ ] Background scheduler running
- [ ] Logs monitored for errors

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

**Important**: This is free and open-source software. You are free to use, modify, and distribute it under the terms of the GPL-3.0 license. Please ensure you comply with both the license terms and Plex's Terms of Service when using this application.

## Support

For issues, questions, or contributions:

- **Bug Reports**: Open an issue on GitHub
- **Feature Requests**: Open an issue with the "enhancement" label
- **Security Issues**: See [SECURITY.md](SECURITY.md) for private reporting
- **Stripe Questions**: See [STRIPE_SETUP.md](STRIPE_SETUP.md)
- **General Questions**: Check existing issues or open a discussion
- **Plex API Documentation**: https://python-plexapi.readthedocs.io/
- **Stripe API Documentation**: https://stripe.com/docs/api

## Documentation

- **[README.md](README.md)** - This file (overview and quick start)
- **[STRIPE_SETUP.md](STRIPE_SETUP.md)** - Complete Stripe configuration guide
- **[SUBSCRIPTION_IMPLEMENTATION.md](SUBSCRIPTION_IMPLEMENTATION.md)** - Technical implementation details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[SECURITY.md](SECURITY.md)** - Security policy and reporting
- **[memory-bank/](memory-bank/)** - Project context and history

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Plex integration via [Python-PlexAPI](https://python-plexapi.readthedocs.io/)
- Payment processing by [Stripe](https://stripe.com/)
- Background jobs with [APScheduler](https://apscheduler.readthedocs.io/)
- UI styled with [Bootstrap 5](https://getbootstrap.com/)

