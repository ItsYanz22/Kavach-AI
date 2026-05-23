<#
.SYNOPSIS
Deploys Kavach AI to Google Cloud Run.

.DESCRIPTION
This script automates the deployment of the Kavach AI platform to Google Cloud Run.
It assumes you have the Google Cloud CLI (gcloud) installed and configured.

.PARAMETER ProjectId
Your Google Cloud Project ID (Optional). If not provided, it uses your currently configured default project.

.PARAMETER Region
The Google Cloud region to deploy to (Default: us-central1).
#>
param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Preparing to deploy Kavach AI to Google Cloud Run..." -ForegroundColor Cyan

# 1. Verify gcloud is installed
if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Google Cloud CLI (gcloud) is not installed or not in your PATH." -ForegroundColor Red
    Write-Host "Please download it from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# 2. Check Groq API Key
if (!(Test-Path "backend\.env")) {
    Write-Host "⚠️ Warning: backend\.env file not found. Ensure you have your GROQ_API_KEY ready to input when prompted by Cloud Run." -ForegroundColor Yellow
} else {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -notmatch "GROQ_API_KEY=") {
        Write-Host "⚠️ Warning: GROQ_API_KEY not found in backend\.env." -ForegroundColor Yellow
    }
}

# 3. Configure Project (if provided)
if ($ProjectId) {
    Write-Host "Setting Google Cloud project to: $ProjectId"
    gcloud config set project $ProjectId
} else {
    $currentProject = gcloud config get-value project 2>$null
    if ([string]::IsNullOrWhiteSpace($currentProject)) {
        Write-Host "❌ Error: No default Google Cloud project is set." -ForegroundColor Red
        Write-Host "Run 'gcloud init' or pass the project ID via: .\deploy.ps1 -ProjectId YOUR_PROJECT_ID"
        exit 1
    }
    Write-Host "Using default Google Cloud project: $currentProject"
}

# 4. Build and Deploy
Write-Host "📦 Building and deploying the container... (This may take a few minutes)" -ForegroundColor Cyan
Write-Host "Executing: gcloud run deploy kavach-ai --source . --platform managed --region $Region --allow-unauthenticated"

# Cloud Run will automatically find Dockerfile.production if we tell it to via environment variables, 
# or since it might default to Dockerfile, let's explicitly specify the Dockerfile using a gcloud builds submit
Write-Host "Step 1: Submitting build to Cloud Build..."
$ImageName = "gcr.io/$(gcloud config get-value project)/kavach-ai:latest"
gcloud builds submit --tag $ImageName -f Dockerfile.production

Write-Host "Step 2: Deploying image to Cloud Run..."
gcloud run deploy kavach-ai `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --set-env-vars="ENVIRONMENT=production"

Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "Make sure to set your GROQ_API_KEY and JWT_SECRET_KEY in the Cloud Run console:"
Write-Host "1. Go to https://console.cloud.google.com/run"
Write-Host "2. Select 'kavach-ai'"
Write-Host "3. Click 'Edit & Deploy New Revision'"
Write-Host "4. Under 'Variables & Secrets', add your GROQ_API_KEY"
Write-Host "5. Click Deploy"

