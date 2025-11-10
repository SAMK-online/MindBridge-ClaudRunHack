#!/bin/bash

# MindBridge - Cloud Run Deployment Script
# Usage: ./deploy.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════╗"
echo "║   MindBridge - Cloud Run Deployment Script   ║"
echo "╔═══════════════════════════════════════════════╗"
echo -e "${NC}"

# Configuration
PROJECT_ID="nimacareai"
SERVICE_NAME="mindbridge"
REGION="us-central1"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI not found${NC}"
    echo -e "${YELLOW}Please install Google Cloud SDK:${NC}"
    echo -e "  macOS: ${BLUE}curl https://sdk.cloud.google.com | bash${NC}"
    echo -e "  Or:    ${BLUE}brew install --cask google-cloud-sdk${NC}"
    echo ""
    echo -e "  Windows: Download from https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✓${NC} Google Cloud SDK found"

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}⚠ Not authenticated with Google Cloud${NC}"
    echo "Running: gcloud auth login"
    gcloud auth login
fi

echo -e "${GREEN}✓${NC} Authenticated with Google Cloud"

# Set project
echo ""
echo -e "${BLUE}Setting project to: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID}

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env with your API keys, then run this script again${NC}"
    exit 1
fi

# Load environment variables
source .env

# Validate API key
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your_gemini_api_key_here" ]; then
    echo -e "${RED}❌ Error: GOOGLE_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}Please edit .env and set your Gemini API key${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Environment variables loaded"

# Enable required APIs
echo ""
echo -e "${BLUE}Enabling required Google Cloud APIs...${NC}"
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

echo -e "${GREEN}✓${NC} APIs enabled"

# Confirm deployment
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Deployment Configuration:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════${NC}"
echo -e "  Project:  ${BLUE}${PROJECT_ID}${NC}"
echo -e "  Service:  ${BLUE}${SERVICE_NAME}${NC}"
echo -e "  Region:   ${BLUE}${REGION}${NC}"
echo -e "  Memory:   ${BLUE}2Gi${NC}"
echo -e "  CPU:      ${BLUE}2 vCPU${NC}"
echo -e "  Timeout:  ${BLUE}300s${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════${NC}"
echo ""

read -p "Deploy to Cloud Run? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Deploy to Cloud Run
echo ""
echo -e "${BLUE}🚀 Deploying to Cloud Run...${NC}"
echo ""

gcloud run deploy ${SERVICE_NAME} \
  --source . \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
  --set-env-vars GOOGLE_CLOUD_PROJECT="${PROJECT_ID}" \
  --set-env-vars PORT="8080"

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     🎉 Deployment Successful! 🎉              ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
        --region ${REGION} \
        --format 'value(status.url)')
    
    echo -e "${BLUE}Service URL:${NC} ${GREEN}${SERVICE_URL}${NC}"
    echo ""
    echo -e "${YELLOW}Quick Links:${NC}"
    echo -e "  Landing Page:     ${BLUE}${SERVICE_URL}/${NC}"
    echo -e "  Voice Interface:  ${BLUE}${SERVICE_URL}/app${NC}"
    echo -e "  Text Chat:        ${BLUE}${SERVICE_URL}/chat-ui${NC}"
    echo -e "  API Docs:         ${BLUE}${SERVICE_URL}/docs${NC}"
    echo -e "  Health Check:     ${BLUE}${SERVICE_URL}/health${NC}"
    echo ""
    
    # Test health endpoint
    echo -e "${BLUE}Testing health endpoint...${NC}"
    if curl -s "${SERVICE_URL}/health" | grep -q "healthy"; then
        echo -e "${GREEN}✓${NC} Service is healthy!"
    else
        echo -e "${YELLOW}⚠ Service deployed but health check failed${NC}"
        echo "Check logs: gcloud run services logs read ${SERVICE_NAME} --region ${REGION}"
    fi
    
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Visit ${SERVICE_URL} to see your landing page"
    echo "  2. Test the voice interface at ${SERVICE_URL}/app"
    echo "  3. Update GitHub README with live URL"
    echo "  4. Create demo video for hackathon"
    echo ""
    echo -e "${BLUE}View logs:${NC}"
    echo "  gcloud run services logs read ${SERVICE_NAME} --region ${REGION} --follow"
    echo ""
    echo -e "${BLUE}Update deployment:${NC}"
    echo "  ./deploy.sh"
    echo ""
    
else
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║     ❌ Deployment Failed ❌                    ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Check the error messages above${NC}"
    echo ""
    echo -e "${BLUE}Common fixes:${NC}"
    echo "  1. Verify billing is enabled for project"
    echo "  2. Check API key is valid"
    echo "  3. Ensure you have necessary permissions"
    echo "  4. Review logs: gcloud run services logs read ${SERVICE_NAME}"
    echo ""
    exit 1
fi

