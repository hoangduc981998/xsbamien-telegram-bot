#!/bin/bash
#
# Deploy xsbamien-telegram-bot to Google Cloud Run
#
# Usage: ./scripts/deploy.sh [environment]
# Example: ./scripts/deploy.sh production
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
PROJECT_ID=${GCP_PROJECT_ID:-""}
REGION=${GCP_REGION:-"asia-southeast1"}
SERVICE_NAME="xsbamien-telegram-bot"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  XS Ba Miền - Deployment Script${NC}"
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

# Step 1: Validate environment variables
print_info "Step 1: Validating environment variables..."

if [ -z "$PROJECT_ID" ]; then
    print_error "GCP_PROJECT_ID environment variable is not set"
    print_info "Please set it with: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ] && [ "$ENVIRONMENT" != "test" ]; then
    print_warning "TELEGRAM_BOT_TOKEN not set (required for deployment)"
fi

print_success "Environment: $ENVIRONMENT"
print_success "Project ID: $PROJECT_ID"
print_success "Region: $REGION"
print_success "Service Name: $SERVICE_NAME"
echo ""

# Step 2: Build Docker image
print_info "Step 2: Building Docker image..."

COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
IMAGE_TAG="${IMAGE_NAME}:${COMMIT_SHA}"
IMAGE_LATEST="${IMAGE_NAME}:latest"

docker build -t "$IMAGE_TAG" -t "$IMAGE_LATEST" . || {
    print_error "Docker build failed"
    exit 1
}

print_success "Docker image built successfully"
print_info "Image tags: $IMAGE_TAG, $IMAGE_LATEST"
echo ""

# Step 3: Push to Google Container Registry
print_info "Step 3: Pushing image to Google Container Registry..."

# Configure Docker for GCR
gcloud auth configure-docker --quiet || {
    print_error "Failed to configure Docker for GCR"
    exit 1
}

docker push "$IMAGE_TAG" || {
    print_error "Failed to push image: $IMAGE_TAG"
    exit 1
}

docker push "$IMAGE_LATEST" || {
    print_error "Failed to push image: $IMAGE_LATEST"
    exit 1
}

print_success "Image pushed to GCR"
echo ""

# Step 4: Deploy to Cloud Run
print_info "Step 4: Deploying to Cloud Run..."

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080 \
    --set-env-vars "ENVIRONMENT=${ENVIRONMENT},LOG_LEVEL=INFO" \
    --set-secrets "TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest" \
    --quiet || {
    print_error "Deployment failed"
    exit 1
}

print_success "Deployment completed"
echo ""

# Step 5: Get service URL
print_info "Step 5: Getting service URL..."

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --format 'value(status.url)') || {
    print_error "Failed to get service URL"
    exit 1
}

print_success "Service URL: $SERVICE_URL"
echo ""

# Step 6: Verify deployment
print_info "Step 6: Verifying deployment..."

sleep 5  # Wait for service to be ready

if curl -f "${SERVICE_URL}/health" > /dev/null 2>&1; then
    print_success "Health check passed"
else
    print_warning "Health check failed (service may still be starting)"
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Deployment Successful!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "Service URL: ${BLUE}${SERVICE_URL}${NC}"
echo -e "Image: ${BLUE}${IMAGE_TAG}${NC}"
echo -e "Commit: ${BLUE}${COMMIT_SHA}${NC}"
echo ""
echo "To view logs:"
echo "  gcloud run logs read ${SERVICE_NAME} --region ${REGION} --limit 50"
echo ""
echo "To view service details:"
echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION}"
echo ""
