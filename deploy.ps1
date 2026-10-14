<#
.SYNOPSIS
Deploys Kavach AI to Google Cloud Run.

.DESCRIPTION
This script builds the Kavach AI container using Google Cloud Build and deploys it to Cloud Run.
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

Write-Host "[INFO] Preparing to deploy Kavach AI to Google Cloud Run..." -ForegroundColor Cyan

# 1. Verify gcloud is installed
if (!(Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Google Cloud CLI (gcloud) is not installed or not in your PATH." -ForegroundColor Red
    Write-Host "Please download it from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# 2. Check Groq API Key
if (!(Test-Path "backend\.env")) {
    Write-Host "[WARN] backend\.env file not found. Ensure GROQ_API_KEY is configured in Cloud Run." -ForegroundColor Yellow
} else {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -notmatch "GROQ_API_KEY=") {
        Write-Host "[WARN] GROQ_API_KEY not found in backend\.env." -ForegroundColor Yellow
    }
}

# 3. Configure Project (if provided)
if ($ProjectId) {
    Write-Host "[INFO] Setting Google Cloud project to: $ProjectId"
    gcloud config set project $ProjectId
} else {
    $currentProject = gcloud config get-value project 2>$null
    if ([string]::IsNullOrWhiteSpace($currentProject)) {
        Write-Host "[ERROR] No default Google Cloud project is set." -ForegroundColor Red
        Write-Host "Run 'gcloud init' or pass the project ID via: .\deploy.ps1 -ProjectId YOUR_PROJECT_ID"
        exit 1
    }
    Write-Host "[INFO] Using Google Cloud project: $currentProject"
}

$Project = gcloud config get-value project
$ImageName = "gcr.io/$Project/kavach-ai:latest"

# 4. Build and Deploy
Write-Host "[INFO] Step 1: Submitting build to Cloud Build..." -ForegroundColor Cyan
Write-Host "Building image: $ImageName from current directory Dockerfile..."
gcloud builds submit --tag $ImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Cloud Build failed with exit code $LASTEXITCODE." -ForegroundColor Red
    Write-Host "[HINT] If you see BILLING_DISABLED or 403, visit: https://console.developers.google.com/billing/enable?project=$Project" -ForegroundColor Yellow
    exit $LASTEXITCODE
}

Write-Host "[INFO] Step 2: Deploying image to Cloud Run..." -ForegroundColor Cyan
gcloud run deploy kavach-ai `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --update-env-vars="ENVIRONMENT=production"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Cloud Run deploy failed with exit code $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[SUCCESS] Deployment Complete!" -ForegroundColor Green
$ServiceUrl = gcloud run services describe kavach-ai --region $Region --format="value(status.url)"
Write-Host "[INFO] Service URL: $ServiceUrl" -ForegroundColor Cyan
