# Azure Deployment Script for Plex Invite Application
# This script creates all necessary Azure resources and deploys the application

param(
    [string]$ResourceGroup = "rg-plex-invite-prod",
    [string]$Location = "eastus",
    [string]$AppServicePlan = "asp-plex-invite",
    [string]$WebAppName = "app-plex-invite-$(Get-Random -Maximum 9999)",
    [string]$PostgresServer = "psql-plex-invite-$(Get-Random -Maximum 9999)",
    [string]$DatabaseName = "plexinvitedb",
    [string]$AdminUsername = "plexadmin",
    [string]$Tier = "B1"
)

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Plex Invite Application - Azure Deployment" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check if logged in to Azure
Write-Host "Checking Azure CLI login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Azure. Please login first." -ForegroundColor Red
    az login --tenant cb9ae739-e51a-478f-9b86-6d1f5d67f73c
}

Write-Host "✅ Logged in to Azure" -ForegroundColor Green
Write-Host ""

# Display deployment plan
Write-Host "Deployment Configuration:" -ForegroundColor Cyan
Write-Host "  Resource Group:  $ResourceGroup" -ForegroundColor White
Write-Host "  Location:        $Location" -ForegroundColor White
Write-Host "  App Service:     $WebAppName" -ForegroundColor White
Write-Host "  Database Server: $PostgresServer" -ForegroundColor White
Write-Host "  Tier:            $Tier" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continue with deployment? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Phase 1: Creating Resource Group" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

az group create `
    --name $ResourceGroup `
    --location $Location

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Resource Group created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create Resource Group" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Phase 2: Creating PostgreSQL Flexible Server" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Generate a strong random password
$Password = -join ((65..90) + (97..122) + (48..57) + (33,35,36,37,38,42) | Get-Random -Count 16 | % {[char]$_})

Write-Host "Creating PostgreSQL server (this may take 5-10 minutes)..." -ForegroundColor Yellow

az postgres flexible-server create `
    --name $PostgresServer `
    --resource-group $ResourceGroup `
    --location $Location `
    --admin-user $AdminUsername `
    --admin-password $Password `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 16 `
    --public-access 0.0.0.0-255.255.255.255

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL server created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create PostgreSQL server" -ForegroundColor Red
    exit 1
}

# Create database
Write-Host "Creating database..." -ForegroundColor Yellow
az postgres flexible-server db create `
    --resource-group $ResourceGroup `
    --server-name $PostgresServer `
    --database-name $DatabaseName

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create database" -ForegroundColor Red
}

# Build connection string
$ConnectionString = "postgresql://${AdminUsername}:${Password}@${PostgresServer}.postgres.database.azure.com/${DatabaseName}?sslmode=require"

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Phase 3: Creating App Service Plan" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

az appservice plan create `
    --name $AppServicePlan `
    --resource-group $ResourceGroup `
    --location $Location `
    --sku $Tier `
    --is-linux

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ App Service Plan created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create App Service Plan" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Phase 4: Creating Web App" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

az webapp create `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --plan $AppServicePlan `
    --runtime "PYTHON:3.11"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Web App created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create Web App" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Phase 5: Configuring Application Settings" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Read current .env file values
Write-Host "Reading configuration from .env file..." -ForegroundColor Yellow

$envContent = Get-Content .env -ErrorAction SilentlyContinue
$envVars = @{}

if ($envContent) {
    foreach ($line in $envContent) {
        if ($line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -and $value -and -not $key.StartsWith('#')) {
                $envVars[$key] = $value
            }
        }
    }
}

# Configure app settings
$settings = @(
    "DATABASE_URL=$ConnectionString"
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS=7"
)

# Add environment variables from .env
foreach ($key in @('SECRET_KEY', 'PLEX_TOKEN', 'PLEX_SERVER_NAME', 'ADMIN_USERNAME', 'ADMIN_PASSWORD_HASH', 'INVITE_CODE')) {
    if ($envVars.ContainsKey($key)) {
        $settings += "${key}=$($envVars[$key])"
    }
}

az webapp config appsettings set `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --settings $settings

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Application settings configured" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to configure application settings" -ForegroundColor Red
}

# Set startup command
az webapp config set `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --startup-file "startup.sh"

Write-Host "✅ Startup command configured" -ForegroundColor Green

# Enable HTTPS only
az webapp update `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --https-only true

Write-Host "✅ HTTPS-only enabled" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Phase 6: Deploying Application Code" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host "Deploying code (this may take a few minutes)..." -ForegroundColor Yellow

az webapp up `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --runtime "PYTHON:3.11" `
    --sku $Tier

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Application deployed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to deploy application" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Application URL: https://${WebAppName}.azurewebsites.net" -ForegroundColor Cyan
Write-Host "Admin Login:     https://${WebAppName}.azurewebsites.net/admin/login" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database Connection Information:" -ForegroundColor Yellow
Write-Host "  Server:   ${PostgresServer}.postgres.database.azure.com" -ForegroundColor White
Write-Host "  Database: ${DatabaseName}" -ForegroundColor White
Write-Host "  Username: ${AdminUsername}" -ForegroundColor White
Write-Host "  Password: ${Password}" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANT: Save the database password securely!" -ForegroundColor Red
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  az webapp log tail --name $WebAppName --resource-group $ResourceGroup" -ForegroundColor White
Write-Host ""

