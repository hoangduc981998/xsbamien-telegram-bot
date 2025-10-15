#!/bin/bash
#
# Setup Google Cloud Platform for xsbamien-telegram-bot
# This script enables required APIs, creates service accounts, and sets up secrets
#
# Usage: ./scripts/setup-gcp.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  XS Ba Miền - GCP Setup Script${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if PROJECT_ID is set
if [ -z "$GCP_PROJECT_ID" ]; then
    print_error "GCP_PROJECT_ID environment variable is not set"
    echo ""
    echo "Please set it with:"
    echo "  export GCP_PROJECT_ID=your-project-id"
    echo ""
    exit 1
fi

PROJECT_ID=$GCP_PROJECT_ID
SERVICE_ACCOUNT_NAME="xsbamien-bot-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

print_info "Project ID: $PROJECT_ID"
print_info "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Step 1: Set the active project
print_info "Step 1: Setting active GCP project..."
gcloud config set project "$PROJECT_ID" || {
    print_error "Failed to set project"
    exit 1
}
print_success "Project set to: $PROJECT_ID"
echo ""

# Step 2: Enable required APIs
print_info "Step 2: Enabling required Google Cloud APIs..."

APIS=(
    "run.googleapis.com"               # Cloud Run
    "containerregistry.googleapis.com" # Container Registry
    "cloudbuild.googleapis.com"        # Cloud Build
    "secretmanager.googleapis.com"     # Secret Manager
    "cloudresourcemanager.googleapis.com" # Resource Manager
    "iam.googleapis.com"               # IAM
    "logging.googleapis.com"           # Cloud Logging
    "monitoring.googleapis.com"        # Cloud Monitoring
)

for api in "${APIS[@]}"; do
    print_info "Enabling $api..."
    gcloud services enable "$api" --project="$PROJECT_ID" || {
        print_warning "Failed to enable $api (may already be enabled)"
    }
done

print_success "APIs enabled"
echo ""

# Step 3: Create service account
print_info "Step 3: Creating service account..."

if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" > /dev/null 2>&1; then
    print_warning "Service account already exists: $SERVICE_ACCOUNT_EMAIL"
else
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name "XS Ba Mien Telegram Bot Service Account" \
        --description "Service account for xsbamien-telegram-bot" \
        --project="$PROJECT_ID" || {
        print_error "Failed to create service account"
        exit 1
    }
    print_success "Service account created: $SERVICE_ACCOUNT_EMAIL"
fi
echo ""

# Step 4: Set IAM permissions
print_info "Step 4: Setting IAM permissions..."

ROLES=(
    "roles/run.admin"                  # Cloud Run Admin
    "roles/storage.admin"              # Storage Admin (for GCR)
    "roles/secretmanager.secretAccessor" # Secret Manager Secret Accessor
    "roles/cloudbuild.builds.editor"   # Cloud Build Editor
    "roles/logging.logWriter"          # Logs Writer
)

for role in "${ROLES[@]}"; do
    print_info "Granting $role..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="$role" \
        --quiet > /dev/null || {
        print_warning "Failed to grant $role"
    }
done

print_success "IAM permissions set"
echo ""

# Step 5: Create secrets in Secret Manager
print_info "Step 5: Creating secrets in Secret Manager..."

# Create TELEGRAM_BOT_TOKEN secret
if gcloud secrets describe TELEGRAM_BOT_TOKEN --project="$PROJECT_ID" > /dev/null 2>&1; then
    print_warning "Secret TELEGRAM_BOT_TOKEN already exists"
else
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        print_warning "TELEGRAM_BOT_TOKEN not set in environment"
        print_info "Creating empty secret (you can add the value later)"
        echo -n "" | gcloud secrets create TELEGRAM_BOT_TOKEN \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID" || {
            print_error "Failed to create TELEGRAM_BOT_TOKEN secret"
        }
    else
        echo -n "$TELEGRAM_BOT_TOKEN" | gcloud secrets create TELEGRAM_BOT_TOKEN \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID" || {
            print_error "Failed to create TELEGRAM_BOT_TOKEN secret"
        }
        print_success "Secret TELEGRAM_BOT_TOKEN created with value"
    fi
fi

# Grant service account access to secrets
print_info "Granting service account access to secrets..."
gcloud secrets add-iam-policy-binding TELEGRAM_BOT_TOKEN \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID" \
    --quiet > /dev/null || {
    print_warning "Failed to grant secret access"
}

print_success "Secrets configured"
echo ""

# Step 6: Download service account key
print_info "Step 6: Creating service account key..."

KEY_FILE="gcp-key.json"
if [ -f "$KEY_FILE" ]; then
    print_warning "Key file already exists: $KEY_FILE"
    read -p "Do you want to overwrite it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping key creation"
    else
        gcloud iam service-accounts keys create "$KEY_FILE" \
            --iam-account="$SERVICE_ACCOUNT_EMAIL" \
            --project="$PROJECT_ID" || {
            print_error "Failed to create service account key"
            exit 1
        }
        print_success "Service account key created: $KEY_FILE"
        print_warning "Keep this file secure and DO NOT commit it to git!"
    fi
else
    gcloud iam service-accounts keys create "$KEY_FILE" \
        --iam-account="$SERVICE_ACCOUNT_EMAIL" \
        --project="$PROJECT_ID" || {
        print_error "Failed to create service account key"
        exit 1
    }
    print_success "Service account key created: $KEY_FILE"
    print_warning "Keep this file secure and DO NOT commit it to git!"
fi
echo ""

# Summary
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  GCP Setup Completed!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Summary:"
echo "  • Project ID: $PROJECT_ID"
echo "  • Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "  • Secrets: TELEGRAM_BOT_TOKEN"
echo ""
echo "Next steps:"
echo "  1. Add service account key to GitHub secrets as GCP_SA_KEY:"
if [ -f "$KEY_FILE" ]; then
    echo "     cat $KEY_FILE | base64"
fi
echo ""
echo "  2. Add project ID to GitHub secrets as GCP_PROJECT_ID:"
echo "     $PROJECT_ID"
echo ""
echo "  3. If you haven't set the bot token secret value yet:"
echo "     echo -n 'YOUR_BOT_TOKEN' | gcloud secrets versions add TELEGRAM_BOT_TOKEN --data-file=-"
echo ""
echo "  4. Deploy the bot:"
echo "     ./scripts/deploy.sh production"
echo ""
