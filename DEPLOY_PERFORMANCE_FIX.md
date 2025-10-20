# Deploy Performance Fixes to Azure Container App

## Changes Pushed to GitHub ✅
- Commit: `ca305d3`
- Branch: `main`
- Changes: Performance optimizations for Plex API connections

---

## Option 1: Quick Deploy via Azure Portal (Recommended)

If your Container App is set up for continuous deployment from GitHub:

1. **Go to Azure Portal**:
   - Navigate to: https://portal.azure.com
   - Resource Group: `rg-plex-invite`
   - Container App: `plex-invite-app`

2. **Check Continuous Deployment**:
   - Go to "Continuous deployment" in the left menu
   - If connected to GitHub, it may auto-deploy (wait 5-10 minutes)

3. **Manual Revision**:
   - If not auto-deployed, go to "Revision management"
   - Click "Create new revision"
   - Select your existing container
   - Click "Create" (this will use latest image)

---

## Option 2: Rebuild Container via Azure Cloud Shell

If you need to manually rebuild the container image:

### Step 1: Open Azure Cloud Shell
Go to: https://shell.azure.com (or click the `>_` icon in Azure Portal)

### Step 2: Clone/Pull Latest Code
```bash
# If you haven't cloned the repo yet:
git clone https://github.com/misterentity/helpr.git
cd helpr

# Or if already cloned:
cd helpr
git pull origin main
```

### Step 3: Find Your Container Registry
```bash
# List your container registries
az acr list --resource-group rg-plex-invite --output table

# Or list all ACRs in subscription
az acr list --output table
```

### Step 4: Build New Container Image
Replace `<your-acr-name>` with your Azure Container Registry name:

```bash
# Build and push the new image
az acr build --registry <your-acr-name> \
  --image plex-invite:latest \
  --image plex-invite:v1.1-performance \
  --file Dockerfile \
  .
```

Example:
```bash
az acr build --registry myregistry123 \
  --image plex-invite:latest \
  --image plex-invite:v1.1-performance \
  --file Dockerfile \
  .
```

### Step 5: Update Container App
```bash
# Update the container app to use the new image
az containerapp update \
  --name plex-invite-app \
  --resource-group rg-plex-invite \
  --image <your-acr-name>.azurecr.io/plex-invite:latest
```

Example:
```bash
az containerapp update \
  --name plex-invite-app \
  --resource-group rg-plex-invite \
  --image myregistry123.azurecr.io/plex-invite:latest
```

---

## Option 3: GitHub Actions (Best for Future)

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure Container App

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and push image
        run: |
          az acr build --registry <your-acr> \
            --image plex-invite:${{ github.sha }} \
            --image plex-invite:latest \
            .
      
      - name: Deploy to Container App
        run: |
          az containerapp update \
            --name plex-invite-app \
            --resource-group rg-plex-invite \
            --image <your-acr>.azurecr.io/plex-invite:latest
```

Then future pushes will auto-deploy!

---

## Option 4: If You Don't Have ACR

If you don't have an Azure Container Registry, you can use Docker Hub or create one:

### Create ACR (One-time setup):
```bash
az acr create \
  --name plexinviteregistry \
  --resource-group rg-plex-invite \
  --sku Basic \
  --admin-enabled true
```

Then follow Option 2 steps above.

---

## Verify Deployment

After deployment (wait 2-3 minutes for app to restart):

1. **Check App Status**:
   ```bash
   az containerapp show \
     --name plex-invite-app \
     --resource-group rg-plex-invite \
     --query "properties.latestRevisionName"
   ```

2. **View Logs**:
   - Portal: Container App → Log stream
   - Or CLI: `az containerapp logs tail --name plex-invite-app --resource-group rg-plex-invite`

3. **Test Performance**:
   - Visit: https://plex-invite-app.lemonmushroom-ac327abd.eastus.azurecontainerapps.io/admin/login
   - Log in and verify dashboard loads in < 2 seconds
   - Check logs for "Successfully connected to Plex server" (should appear once per request)

---

## Expected Improvements After Deployment

- ✅ Dashboard load time: < 2 seconds (from 3-5+ seconds)
- ✅ Plex API calls reduced by 50-66%
- ✅ No more redundant connections
- ✅ Faster invite processing

---

## Rollback (If Needed)

If something goes wrong, rollback to previous revision:

```bash
# List revisions
az containerapp revision list \
  --name plex-invite-app \
  --resource-group rg-plex-invite \
  --output table

# Activate previous revision
az containerapp revision activate \
  --revision <previous-revision-name> \
  --resource-group rg-plex-invite
```

---

## Need Help?

If you encounter issues:

1. **Check Container App logs** in Portal
2. **Verify environment variables** are still set after deployment
3. **Ensure Plex token is valid** (`PLEX_TOKEN`)
4. **Check startup logs** for any errors

The performance fixes are backward-compatible and require no configuration changes.

