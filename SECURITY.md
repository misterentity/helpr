# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in Helpr, please report it privately to help us address it before public disclosure.

### How to Report

1. **Email**: Send details to the repository maintainer (check GitHub profile for contact)
2. **GitHub Security Advisories**: Use GitHub's "Security" tab → "Report a vulnerability"

### What to Include

Please include as much of the following information as possible:
- Type of vulnerability
- Step-by-step instructions to reproduce
- Affected versions
- Potential impact
- Suggested fix (if you have one)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: Best effort

### Disclosure Policy

- We request that you give us reasonable time to address the issue before public disclosure
- We will credit you in the security advisory (unless you prefer to remain anonymous)
- We will publish a security advisory once the fix is released

## Security Best Practices

When deploying Helpr, please follow these security best practices:

### Environment Variables

- **Never commit `.env` files** to version control
- **Use strong, unique SECRET_KEY**: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- **Protect your PLEX_TOKEN**: Treat it like a password
- **Use strong admin passwords**: Hash with scrypt/bcrypt, never store plaintext

### Production Deployment

- **Always use HTTPS**: Deploy behind a reverse proxy with SSL/TLS
- **Enable rate limiting**: Already built-in, but configure appropriately
- **Use strong database passwords**: If using PostgreSQL
- **Restrict network access**: Firewall rules, VPC, security groups
- **Keep dependencies updated**: Run `pip list --outdated` regularly
- **Monitor logs**: Watch for suspicious activity

### Plex Server Security

- **Secure your Plex server**: Enable authentication, use strong passwords
- **Limit library access**: Only share necessary libraries
- **Review shared users**: Periodically audit who has access
- **Regenerate tokens**: If compromised, regenerate Plex token immediately

### Application Security

- **CSRF Protection**: Enabled by default (Flask-WTF)
- **Rate Limiting**: Configured (Flask-Limiter)
- **Input Validation**: Sanitization on all user inputs
- **SQL Injection**: Protected by SQLAlchemy ORM
- **XSS Protection**: Jinja2 auto-escaping enabled

## Known Security Considerations

### Plex Token Exposure

The Plex token grants full access to your Plex account. If exposed:
1. Regenerate immediately in Plex settings
2. Update the `PLEX_TOKEN` environment variable
3. Restart the application
4. Review Plex account activity for unauthorized access

### Invite Code Security

If using an optional invite code:
- Change it periodically
- Don't share publicly
- Use a strong, random code
- Consider using unique invite links (future feature)

### Database Security

SQLite (default):
- File permissions should be restricted (600)
- Not suitable for high-traffic production
- Data not encrypted at rest

PostgreSQL (recommended for production):
- Use strong passwords
- Enable SSL connections
- Regular backups
- Keep PostgreSQL updated

## Security Updates

Security updates will be released as patches and documented in:
- GitHub Security Advisories
- Release notes
- This SECURITY.md file

Subscribe to repository releases to stay informed.

## Contact

For security concerns, please use private reporting methods described above rather than public issues or discussions.
