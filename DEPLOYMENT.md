# Deployment Guide

This guide covers deploying Helpr to production environments using Docker and various hosting platforms.

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- PostgreSQL database (recommended for production)
- Domain name with SSL certificate (recommended)
- Plex Media Server with Plex Pass subscription

## Environment Configuration

Create a `.env` file with all required variables (see `env.template` for complete list):

```env
SECRET_KEY=your_secret_key_here
PLEX_TOKEN=your_plex_token_here
PLEX_SERVER_NAME=your_server_name
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_hashed_password
INVITE_CODE=optional_invite_code
```

### Generating Secure Values

**SECRET_KEY** (Flask session encryption):
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**ADMIN_PASSWORD_HASH**:
```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"
```

**PLEX_TOKEN**: See [Finding Your Plex Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

## Docker Deployment

### Using Docker Compose (Recommended)

1. Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - PLEX_TOKEN=${PLEX_TOKEN}
      - PLEX_SERVER_NAME=${PLEX_SERVER_NAME}
      - ADMIN_USERNAME=${ADMIN_USERNAME}
      - ADMIN_PASSWORD_HASH=${ADMIN_PASSWORD_HASH}
      - INVITE_CODE=${INVITE_CODE}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./invites.db:/app/invites.db
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: helpr
      POSTGRES_USER: helpr
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

2. Create `.env` file with your configuration

3. Build and start:
```bash
docker-compose up -d
```

4. View logs:
```bash
docker-compose logs -f
```

### Using Docker Directly

1. Build the image:
```bash
docker build -t helpr:latest .
```

2. Run the container:
```bash
docker run -d \
  --name helpr \
  -p 8000:8000 \
  -e SECRET_KEY="your_secret_key" \
  -e PLEX_TOKEN="your_plex_token" \
  -e PLEX_SERVER_NAME="your_server_name" \
  -e ADMIN_USERNAME="admin" \
  -e ADMIN_PASSWORD_HASH="your_hashed_password" \
  -v $(pwd)/invites.db:/app/invites.db \
  helpr:latest
```

## Database Configuration

### SQLite (Development Only)

Default configuration uses SQLite:
- File stored at `invites.db`
- Not recommended for production (not suitable for concurrent users)
- Data persists only if volume is mounted

### PostgreSQL (Recommended for Production)

Set the DATABASE_URL environment variable:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/helpr
```

Or use individual PostgreSQL environment variables (Azure format):
```bash
AZURE_POSTGRESQL_CONNECTIONSTRING=postgresql://username:password@server.postgres.database.com/helpr?sslmode=require
```

## Reverse Proxy Setup

Always deploy behind a reverse proxy with HTTPS in production.

### Nginx Example

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy Example

```
your-domain.com {
    reverse_proxy localhost:8000
}
```

Caddy automatically handles HTTPS certificates via Let's Encrypt.

## Cloud Platform Deployment

### Generic Container Platform

Helpr can be deployed to any platform supporting Docker containers:

1. **Container Registries**: Push image to Docker Hub, GitHub Container Registry, or private registry
2. **Container Platforms**: Deploy to any service (AWS ECS, Google Cloud Run, Azure Container Apps, DigitalOcean App Platform, Fly.io, Railway, etc.)
3. **Environment Variables**: Configure via platform's environment variable settings
4. **Database**: Use platform's managed PostgreSQL service
5. **Scaling**: Most platforms support auto-scaling based on traffic

### General Steps

1. Build and push Docker image to registry
2. Create managed PostgreSQL database
3. Configure environment variables in platform
4. Deploy container with image from registry
5. Point custom domain with SSL
6. Configure health checks on `/` endpoint
7. Set up monitoring and logging

## Production Checklist

Before going to production:

- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Use strong, unique SECRET_KEY
- [ ] Use strong admin password (hashed)
- [ ] Set up automated backups for database
- [ ] Configure firewall rules
- [ ] Enable monitoring and alerting
- [ ] Test rate limiting is working
- [ ] Test CSRF protection is enabled
- [ ] Review Plex server security settings
- [ ] Document your deployment for team
- [ ] Test invite flow end-to-end
- [ ] Set up log rotation
- [ ] Configure proper file permissions

## Monitoring

Monitor these metrics in production:

- Application uptime
- Response times (dashboard should load < 2 seconds)
- Error rates (500 errors)
- Database connection pool
- Plex API response times
- Rate limit hits
- Failed login attempts

## Backup Strategy

### Database Backups

**PostgreSQL**:
```bash
pg_dump -U username -d helpr > backup_$(date +%Y%m%d).sql
```

**SQLite**:
```bash
cp invites.db invites_backup_$(date +%Y%m%d).db
```

Automate with cron jobs or platform backup features.

### Configuration Backup

- Keep `.env` file backed up securely (encrypted)
- Document all environment variables
- Store Plex token securely (password manager)

## Scaling Considerations

### Horizontal Scaling

Helpr can run multiple instances behind a load balancer:
- Use PostgreSQL (SQLite won't work)
- Sessions stored in database or Redis (future enhancement)
- All instances must use same SECRET_KEY

### Vertical Scaling

Resource requirements:
- **Minimum**: 512MB RAM, 0.5 CPU
- **Recommended**: 1GB RAM, 1 CPU
- **High Traffic**: 2GB RAM, 2 CPU

## Security Hardening

1. **Firewall**: Only expose ports 80/443
2. **Fail2ban**: Block brute force attempts
3. **Rate Limiting**: Already configured, adjust if needed
4. **Database**: Use strong passwords, enable SSL
5. **Updates**: Keep OS and dependencies updated
6. **Monitoring**: Watch for suspicious activity
7. **Backups**: Test restore procedures regularly

## Troubleshooting

### Application Won't Start

- Check environment variables are set
- Verify Plex token is valid
- Check database connectivity
- Review application logs

### Slow Performance

- Check Plex server is responsive
- Verify database connection is fast
- Check network latency to Plex
- Review application logs for errors

### Invite Emails Not Received

- Plex sends the emails (not this app)
- Check Plex server email settings
- Verify user's email is correct
- Check spam folders

## Updates

To update Helpr:

1. Pull latest code: `git pull origin main`
2. Rebuild Docker image: `docker-compose build`
3. Restart containers: `docker-compose up -d`
4. Check logs: `docker-compose logs -f`

Or with Docker:
```bash
docker pull your-registry/helpr:latest
docker stop helpr
docker rm helpr
docker run -d [same parameters as before]
```

## Support

- Report issues: GitHub Issues
- Security concerns: See SECURITY.md
- Contributing: See CONTRIBUTING.md
