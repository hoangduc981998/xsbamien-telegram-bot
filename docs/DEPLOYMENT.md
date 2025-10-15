# 🚀 Deployment Guide - XS Ba Miền Telegram Bot

Comprehensive guide for deploying xsbamien-telegram-bot to production.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Google Cloud Run Deployment](#google-cloud-run-deployment)
5. [GitHub Actions CI/CD](#github-actions-cicd)
6. [Environment Variables](#environment-variables)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)

---

## 1. Prerequisites

### Required Tools
- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
- **Google Cloud SDK** - [Install gcloud](https://cloud.google.com/sdk/docs/install)
- **Git** - [Install Git](https://git-scm.com/downloads)

### Required Accounts
- **Telegram Bot Token** - Get from [@BotFather](https://t.me/BotFather)
- **Google Cloud Platform** - [Create account](https://cloud.google.com/)
- **GitHub Account** - For CI/CD

### GCP Prerequisites
- Active GCP Project with billing enabled
- APIs enabled:
  - Cloud Run API
  - Container Registry API
  - Cloud Build API
  - Secret Manager API

---

## 2. Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/hoangduc981998/xsbamien-telegram-bot.git
cd xsbamien-telegram-bot
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Step 4: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your bot token
nano .env  # or use your favorite editor
```

Required in `.env`:
```bash
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### Step 5: Run Tests
```bash
pytest tests/ -v --cov=app
```

### Step 6: Run Bot Locally
```bash
python -m app.main
```

The bot should start and connect to Telegram. Test it by sending `/start` to your bot.

---

## 3. Docker Deployment

### Local Docker Testing

#### Step 1: Build Docker Image
```bash
docker build -t xsbamien-telegram-bot .
```

#### Step 2: Run with Docker
```bash
docker run --env-file .env xsbamien-telegram-bot
```

#### Step 3: Or Use Docker Compose
```bash
# Start bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop bot
docker-compose down
```

### Docker Compose Features
- Automatic restart on failure
- Volume mounts for logs
- Health checks
- Environment variable management

---

## 4. Google Cloud Run Deployment

### Option A: Automated Setup (Recommended)

#### Step 1: Set Project ID
```bash
export GCP_PROJECT_ID=your-project-id
export TELEGRAM_BOT_TOKEN=your_bot_token
```

#### Step 2: Run Setup Script
```bash
./scripts/setup-gcp.sh
```

This script will:
- ✅ Enable required GCP APIs
- ✅ Create service account
- ✅ Set IAM permissions
- ✅ Create secrets in Secret Manager
- ✅ Generate service account key

#### Step 3: Deploy
```bash
./scripts/deploy.sh production
```

### Option B: Manual Setup

#### Step 1: Enable APIs
```bash
gcloud config set project YOUR_PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

#### Step 2: Create Secret
```bash
echo -n "YOUR_BOT_TOKEN" | gcloud secrets create TELEGRAM_BOT_TOKEN \
  --data-file=- \
  --replication-policy="automatic"
```

#### Step 3: Build and Push Image
```bash
# Build image
docker build -t gcr.io/YOUR_PROJECT_ID/xsbamien-telegram-bot .

# Configure Docker for GCR
gcloud auth configure-docker

# Push image
docker push gcr.io/YOUR_PROJECT_ID/xsbamien-telegram-bot
```

#### Step 4: Deploy to Cloud Run
```bash
gcloud run deploy xsbamien-telegram-bot \
  --image gcr.io/YOUR_PROJECT_ID/xsbamien-telegram-bot \
  --region asia-southeast1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --port 8080 \
  --set-env-vars ENVIRONMENT=production,LOG_LEVEL=INFO \
  --set-secrets TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest
```

#### Step 5: Verify Deployment
```bash
# Get service URL
gcloud run services describe xsbamien-telegram-bot \
  --region asia-southeast1 \
  --format 'value(status.url)'

# Check health
curl https://YOUR-SERVICE-URL/health
```

### Alternative: App Engine Deployment

If you prefer App Engine over Cloud Run:

```bash
# Deploy to App Engine
gcloud app deploy app.yaml

# View logs
gcloud app logs tail -s default
```

---

## 5. GitHub Actions CI/CD

### Setup GitHub Secrets

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**

2. Add the following secrets:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `GCP_PROJECT_ID` | Your GCP project ID | From GCP Console |
| `GCP_SA_KEY` | Service account JSON key | From `gcp-key.json` (base64 encoded) |
| `TELEGRAM_BOT_TOKEN` | Your bot token | From [@BotFather](https://t.me/BotFather) |

### Get Service Account Key
```bash
# After running setup-gcp.sh, encode the key
cat gcp-key.json | base64

# Copy the output and paste as GCP_SA_KEY secret
```

### Workflow Files

The repository includes two workflows:

#### 1. **test.yml** - Runs on Pull Requests
- ✅ Matrix testing (Python 3.11, 3.12)
- ✅ Code quality checks (black, flake8, isort, mypy)
- ✅ Test coverage report
- ✅ Coverage comment on PR

#### 2. **deploy.yml** - Runs on Push to Main
- ✅ Run tests
- ✅ Build Docker image
- ✅ Push to GCR
- ✅ Deploy to Cloud Run
- ✅ Verify deployment

### Manual Trigger

To manually trigger a deployment:

```bash
# Push to main branch
git push origin main
```

Or use GitHub UI: **Actions** → **Deploy to Production** → **Run workflow**

---

## 6. Environment Variables

### Required Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (required) | - | `123456:ABC-DEF...` |
| `ENVIRONMENT` | Deployment environment | `production` | `development`, `staging`, `production` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `API_BASE_URL` | Lottery API URL | `https://mu88.live/...` | Custom API URL |
| `API_TIMEOUT` | API request timeout (seconds) | `30` | `60` |
| `API_RETRY_TIMES` | Number of retry attempts | `3` | `5` |
| `CACHE_ENABLED` | Enable caching | `true` | `true`, `false` |
| `CACHE_TYPE` | Cache backend type | `redis` | `redis`, `sqlite`, `memory` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` | `redis://user:pass@host:port` |
| `CACHE_TTL` | Cache TTL (seconds) | `3600` | `7200` |

### Setting in Cloud Run

```bash
# Update environment variables
gcloud run services update xsbamien-telegram-bot \
  --region asia-southeast1 \
  --set-env-vars LOG_LEVEL=DEBUG,CACHE_TTL=7200
```

### Setting in Secret Manager

```bash
# Update secret
echo -n "NEW_TOKEN" | gcloud secrets versions add TELEGRAM_BOT_TOKEN \
  --data-file=-
```

---

## 7. Monitoring & Alerts

### View Logs

#### Cloud Run Logs
```bash
# View recent logs
gcloud run logs read xsbamien-telegram-bot \
  --region asia-southeast1 \
  --limit 50

# Tail logs (follow)
gcloud run logs tail xsbamien-telegram-bot \
  --region asia-southeast1

# Filter by severity
gcloud run logs read xsbamien-telegram-bot \
  --region asia-southeast1 \
  --log-filter "severity>=ERROR"
```

#### Cloud Logging
Go to: [Cloud Logging Console](https://console.cloud.google.com/logs)

Filter query:
```
resource.type="cloud_run_revision"
resource.labels.service_name="xsbamien-telegram-bot"
```

### Health Checks

The bot exposes several health check endpoints:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Basic health check | Status and uptime |
| `/health/live` | Liveness probe | Is service alive? |
| `/health/ready` | Readiness probe | Ready for traffic? |
| `/status` | Full status | Detailed diagnostics |

Test health:
```bash
curl https://YOUR-SERVICE-URL/health
```

### Metrics

View metrics in [Cloud Monitoring](https://console.cloud.google.com/monitoring):

- **Request Count** - Number of requests
- **Request Latency** - Response time
- **Error Rate** - 5xx errors
- **CPU Utilization** - CPU usage
- **Memory Utilization** - Memory usage
- **Instance Count** - Number of instances

### Alerts

Create monitoring alerts from `monitoring/alerts.yaml`:

```bash
# Create alerts (requires gcloud alpha)
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/alerts.yaml
```

Alerts configured:
- ⚠️ High Error Rate (>5%)
- ⚠️ High Latency (>2s)
- ⚠️ High Memory Usage (>80%)
- ⚠️ High CPU Usage (>80%)
- 🚨 Service Down

---

## 8. Troubleshooting

### Bot Not Starting

**Symptom**: Bot doesn't respond to commands

**Solutions**:
1. Check bot token:
   ```bash
   # Verify secret exists
   gcloud secrets versions access latest --secret="TELEGRAM_BOT_TOKEN"
   ```

2. Check logs:
   ```bash
   gcloud run logs read xsbamien-telegram-bot --limit 50
   ```

3. Verify service is running:
   ```bash
   gcloud run services describe xsbamien-telegram-bot \
     --region asia-southeast1
   ```

### High Memory Usage

**Symptom**: Service keeps restarting or OOM errors

**Solutions**:
1. Increase memory:
   ```bash
   gcloud run services update xsbamien-telegram-bot \
     --region asia-southeast1 \
     --memory 1Gi
   ```

2. Check cache configuration:
   - Reduce `CACHE_TTL`
   - Reduce `CACHE_MAX_SIZE` in production config

### API Errors

**Symptom**: Lottery results not loading

**Solutions**:
1. Check API connectivity:
   ```bash
   curl -v https://mu88.live/api/front/open/lottery/history/list/game
   ```

2. Increase timeout:
   ```bash
   gcloud run services update xsbamien-telegram-bot \
     --region asia-southeast1 \
     --set-env-vars API_TIMEOUT=60
   ```

### Deployment Failures

**Symptom**: Deployment fails in GitHub Actions

**Solutions**:
1. Verify secrets are set in GitHub
2. Check service account has correct permissions:
   ```bash
   gcloud projects get-iam-policy YOUR_PROJECT_ID \
     --flatten="bindings[].members" \
     --filter="bindings.members:serviceAccount:xsbamien-bot-sa*"
   ```

3. Check Cloud Build logs:
   ```bash
   gcloud builds list --limit 5
   gcloud builds log BUILD_ID
   ```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid bot token | Update `TELEGRAM_BOT_TOKEN` secret |
| `503 Service Unavailable` | API down or timeout | Increase `API_TIMEOUT`, check API status |
| `429 Too Many Requests` | Rate limiting | Implement rate limiting, reduce requests |
| `Container failed to start` | Startup error | Check logs for Python errors |

---

## 9. Rollback Procedures

### Quick Rollback

If a deployment causes issues, rollback immediately:

#### Option 1: Rollback to Previous Revision
```bash
# List revisions
gcloud run revisions list --service xsbamien-telegram-bot \
  --region asia-southeast1

# Rollback to specific revision
gcloud run services update-traffic xsbamien-telegram-bot \
  --region asia-southeast1 \
  --to-revisions REVISION_NAME=100
```

#### Option 2: Redeploy Previous Image
```bash
# Find previous image
gcloud container images list-tags gcr.io/YOUR_PROJECT_ID/xsbamien-telegram-bot

# Deploy previous image
gcloud run deploy xsbamien-telegram-bot \
  --image gcr.io/YOUR_PROJECT_ID/xsbamien-telegram-bot:PREVIOUS_SHA \
  --region asia-southeast1
```

#### Option 3: Git Revert
```bash
# Revert last commit
git revert HEAD

# Push to main (triggers new deployment)
git push origin main
```

### Gradual Rollout

For safer deployments, use traffic splitting:

```bash
# Deploy new version without routing traffic
gcloud run deploy xsbamien-telegram-bot \
  --image gcr.io/YOUR_PROJECT_ID/xsbamien-telegram-bot:latest \
  --region asia-southeast1 \
  --no-traffic

# Gradually increase traffic to new revision
gcloud run services update-traffic xsbamien-telegram-bot \
  --region asia-southeast1 \
  --to-revisions NEW_REVISION=50,OLD_REVISION=50

# After validation, route all traffic
gcloud run services update-traffic xsbamien-telegram-bot \
  --region asia-southeast1 \
  --to-latest
```

---

## 📚 Additional Resources

### Documentation
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Docs](https://docs.github.com/actions)

### Support
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/hoangduc981998/xsbamien-telegram-bot/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/hoangduc981998/xsbamien-telegram-bot/discussions)
- 📧 **Email**: [Contact form coming soon]

### Monitoring Tools
- [Cloud Run Console](https://console.cloud.google.com/run)
- [Cloud Logging](https://console.cloud.google.com/logs)
- [Cloud Monitoring](https://console.cloud.google.com/monitoring)
- [Container Registry](https://console.cloud.google.com/gcr)

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] ✅ Bot responds to `/start` command
- [ ] ✅ Health check endpoint returns 200 OK
- [ ] ✅ Logs are flowing to Cloud Logging
- [ ] ✅ No errors in recent logs
- [ ] ✅ Monitoring dashboards show metrics
- [ ] ✅ Alerts are configured
- [ ] ✅ Secrets are secured (not in code)
- [ ] ✅ CI/CD pipeline is working
- [ ] ✅ Documentation is up to date

---

**Last Updated**: 2025-10-15  
**Version**: 1.0.0  
**Maintained by**: @hoangduc981998
