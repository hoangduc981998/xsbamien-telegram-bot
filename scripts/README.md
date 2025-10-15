# Deployment Scripts

This directory contains scripts for deploying xsbamien-telegram-bot to production.

## 📜 Available Scripts

### 1. setup-gcp.sh
**Purpose**: Initial setup of Google Cloud Platform for the bot

**Usage**:
```bash
export GCP_PROJECT_ID=your-project-id
export TELEGRAM_BOT_TOKEN=your_bot_token  # Optional
./scripts/setup-gcp.sh
```

**What it does**:
- ✅ Enables required GCP APIs (Cloud Run, Container Registry, Secret Manager, etc.)
- ✅ Creates service account `xsbamien-bot-sa`
- ✅ Assigns necessary IAM roles
- ✅ Creates `TELEGRAM_BOT_TOKEN` secret in Secret Manager
- ✅ Generates service account key file (`gcp-key.json`)

**Prerequisites**:
- Google Cloud SDK installed and authenticated
- GCP project with billing enabled
- `GCP_PROJECT_ID` environment variable set

**Output**:
- Service account created
- `gcp-key.json` file (keep secure, DO NOT commit!)
- Instructions for GitHub Actions setup

---

### 2. deploy.sh
**Purpose**: Deploy the bot to Google Cloud Run

**Usage**:
```bash
export GCP_PROJECT_ID=your-project-id
./scripts/deploy.sh [environment]

# Examples:
./scripts/deploy.sh production
./scripts/deploy.sh staging
```

**What it does**:
- ✅ Validates environment variables
- ✅ Builds Docker image
- ✅ Pushes to Google Container Registry
- ✅ Deploys to Cloud Run
- ✅ Verifies deployment with health check
- ✅ Shows service URL and deployment info

**Prerequisites**:
- Docker installed
- Google Cloud SDK installed and authenticated
- `GCP_PROJECT_ID` environment variable set
- Service account and secrets already created (run `setup-gcp.sh` first)

**Configuration**:
- Default region: `asia-southeast1`
- Memory: 512Mi
- CPU: 1
- Max instances: 10

---

## 🔄 Deployment Workflow

### First Time Setup:
1. **Setup GCP** (one-time):
   ```bash
   export GCP_PROJECT_ID=your-project-id
   export TELEGRAM_BOT_TOKEN=your_bot_token
   ./scripts/setup-gcp.sh
   ```

2. **Configure GitHub Actions** (optional):
   - Add `GCP_PROJECT_ID` to GitHub Secrets
   - Add `GCP_SA_KEY` (from gcp-key.json, base64 encoded) to GitHub Secrets
   - Add `TELEGRAM_BOT_TOKEN` to GitHub Secrets

### Subsequent Deployments:
```bash
./scripts/deploy.sh production
```

Or use GitHub Actions by pushing to main branch.

---

## 🛠️ Troubleshooting

### Script fails with "GCP_PROJECT_ID not set"
**Solution**: Export the environment variable:
```bash
export GCP_PROJECT_ID=your-project-id
```

### Permission denied errors
**Solution**: Make scripts executable:
```bash
chmod +x scripts/*.sh
```

### Docker build fails
**Solution**: Ensure Docker is running and you have internet access

### Deployment fails with authentication errors
**Solution**: Authenticate with gcloud:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Service account key already exists
**Solution**: The script will ask if you want to overwrite it. Choose 'y' or 'n'.

---

## 🔐 Security Notes

- **Never commit `gcp-key.json`** - It contains sensitive credentials
- Store secrets in GCP Secret Manager, not in environment variables
- Use GitHub Secrets for CI/CD credentials
- Rotate service account keys regularly
- Review IAM permissions periodically

---

## 📚 Related Documentation

- [Full Deployment Guide](../docs/DEPLOYMENT.md)
- [README](../README.md)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)

---

**Last Updated**: 2025-10-15  
**Maintained by**: @hoangduc981998
