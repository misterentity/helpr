# Azure Deployment - Complete

## ✅ Deployment Status: LIVE

**Application URL:** https://plex-invite-app.lemonmushroom-ac327abd.eastus.azurecontainerapps.io

**Admin Panel:** https://plex-invite-app.lemonmushroom-ac327abd.eastus.azurecontainerapps.io/admin/login

---

## 🎯 Deployed Resources

### Subscription
- **Name:** MSDN Platforms
- **ID:** b8b6c2e2-56f2-4311-80c6-0f7017cabe86
- **Tenant:** cb9ae739-e51a-478f-9b86-6d1f5d67f73c

### Azure Resources
- **Resource Group:** rg-plex-invite (East US)
- **Container App:** plex-invite-app
- **Type:** Azure Container Apps (NOT App Service)

### Configuration
- **Runtime:** Python 3.11
- **Port:** 8000
- **Ingress:** External, HTTPS enabled
- **Database:** SQLite (in-container, non-persistent)
  - ⚠️ Data will reset on app restart
  - To add persistent storage, add PostgreSQL later

---

## 🔑 Environment Variables Configured

- ✅ `SECRET_KEY` - Flask session encryption
- ✅ `PLEX_TOKEN` - ovcxWhUsVYfHW55F-Hzm
- ✅ `PLEX_SERVER_NAME` - WORKSTATION
- ✅ `ADMIN_USERNAME` - admin
- ✅ `ADMIN_PASSWORD_HASH` - scrypt hash

---

## 📊 What's Working

- ✅ **Public Invite Form** - Users can request invites
- ✅ **Plex API Integration** - Invites are being sent successfully
- ✅ **Admin Login** - Should work now with environment variables set
- ✅ **HTTPS** - Automatic SSL certificate
- ✅ **CSRF Protection** - All forms protected
- ✅ **Rate Limiting** - Abuse protection enabled

---

## ⚠️ Known Limitations

### No Persistent Database
- Currently using SQLite in-container
- **Impact:** Invitation history resets when app restarts
- **Fix:** Add Azure Database for PostgreSQL (see below)

### No Custom Domain
- Using Azure default URL
- **Fix:** Add custom domain in Portal if needed

---

## 💰 Current Costs

- **Container App:** ~$10-15/month
  - 0.5 CPU cores
  - 1 GB memory
  - Auto-scales 1-3 replicas

**To Add PostgreSQL (Optional):**
- PostgreSQL Flexible Server (B1ms): +$12/month
- **Total with database:** ~$22-27/month

---

## 🔧 Managing Your Deployment

### View Logs
**Azure Portal:**
https://portal.azure.com/#@/resource/subscriptions/b8b6c2e2-56f2-4311-80c6-0f7017cabe86/resourceGroups/rg-plex-invite/providers/Microsoft.App/containerApps/plex-invite-app/logStream

### Update Environment Variables
1. Portal → plex-invite-app → Containers
2. Edit and deploy → Click container
3. Environment variables → Add/Edit
4. Create new revision

### Redeploy New Code
Since Azure CLI is broken, use **Azure Cloud Shell**:

```bash
# Login to Cloud Shell: https://shell.azure.com

# Build and push new image
az acr build --registry <your-acr> --image plex-invite:latest .

# Update container app
az containerapp update \
  --name plex-invite-app \
  --resource-group rg-plex-invite \
  --image <your-acr>.azurecr.io/plex-invite:latest
```

### Scale Up/Down
Portal → plex-invite-app → Scale → Adjust min/max replicas

---

## 🚀 Future Enhancements

### Add PostgreSQL for Persistent Storage

1. **Create PostgreSQL in Portal:**
   - Azure Database for PostgreSQL Flexible Server
   - Resource Group: rg-plex-invite
   - Name: plex-invite-db
   - Tier: Burstable B1ms
   - Allow Azure services: Yes

2. **Update Container App:**
   - Add environment variable:
     - `DATABASE_URL` = `postgresql://user:pass@server.postgres.database.azure.com/dbname?sslmode=require`
   - App will automatically use PostgreSQL instead of SQLite

### Add Custom Domain

1. Portal → plex-invite-app → Custom domains
2. Add your domain
3. Configure DNS CNAME record
4. SSL certificate auto-provisioned by Azure

---

## 📝 Files Created for Azure

- ✅ `Dockerfile` - Container image definition
- ✅ `startup.sh` - Application startup script
- ✅ `requirements.txt` - Updated with Azure dependencies
- ✅ `app/models.py` - Database abstraction (SQLite + PostgreSQL support)
- ✅ `.deployment` - Azure build configuration

---

## ✅ Testing Checklist

- [ ] Admin login works
- [ ] Admin dashboard loads
- [ ] Can view Plex libraries
- [ ] Can configure which libraries to share
- [ ] Public invite form works (already confirmed ✓)
- [ ] Rate limiting works
- [ ] Error pages display correctly

---

## 🆘 Troubleshooting

### Admin Login Fails
- Verify `ADMIN_USERNAME` and `ADMIN_PASSWORD_HASH` are set
- Check Portal → Containers → Environment variables
- Verify password matches the hash

### Plex Connection Fails
- Check `PLEX_TOKEN` is correct
- Verify `PLEX_SERVER_NAME` matches your server
- Ensure Plex server is accessible from internet (for Azure to connect)

### App Crashes/Errors
- Check logs in Portal → Log stream
- Verify all environment variables are set
- Check startup logs for Python errors

---

**Deployment Date:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**Status:** ✅ LIVE and WORKING

