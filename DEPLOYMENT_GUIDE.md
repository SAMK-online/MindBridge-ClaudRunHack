# 🚀 MindBridge - Cloud Run Deployment Guide

## Complete Step-by-Step Deployment

---

## Prerequisites Checklist

Before deploying, ensure you have:

- ✅ Google Cloud Account with billing enabled
- ✅ Google Cloud Project (Project ID: `nimacareai`)
- ✅ Gemini API Key
- ⏳ Google Cloud SDK installed

---

## Step 1: Install Google Cloud SDK

### macOS Installation:

```bash
# Download and install
curl https://sdk.cloud.google.com | bash

# Restart your shell
exec -l $SHELL

# Verify installation
gcloud --version
```

### Alternative (Homebrew):

```bash
brew install --cask google-cloud-sdk
```

### Windows Installation:

Download from: https://cloud.google.com/sdk/docs/install

---

## Step 2: Authenticate & Configure

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project nimacareai

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Verify configuration
gcloud config list
```

---

## Step 3: Prepare Environment Variables

Create a `.env.production` file:

```bash
# Copy from example
cp .env.example .env.production

# Edit with production values
nano .env.production
```

**Required Variables:**
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_PROJECT=nimacareai
PORT=8080
ALLOWED_ORIGINS=https://mindbridge-app.run.app,http://localhost:8080
```

---

## Step 4: Deploy to Cloud Run

### Option A: Direct Deploy (Recommended)

```bash
# Navigate to project
cd /Users/abdulshaik/CloudRunHack/MindBridge-ClaudRunHack

# Deploy with source
gcloud run deploy mindbridge \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars GOOGLE_API_KEY="YOUR_API_KEY_HERE" \
  --set-env-vars GOOGLE_CLOUD_PROJECT="nimacareai" \
  --set-env-vars ALLOWED_ORIGINS="https://mindbridge-app.run.app"
```

### Option B: Using Cloud Build

```bash
# Build and deploy using cloudbuild.yaml
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions _GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

### Option C: Docker Build First

```bash
# Build Docker image
docker build -t gcr.io/nimacareai/mindbridge:latest .

# Push to Container Registry
docker push gcr.io/nimacareai/mindbridge:latest

# Deploy from registry
gcloud run deploy mindbridge \
  --image gcr.io/nimacareai/mindbridge:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

---

## Step 5: Verify Deployment

After deployment completes, you'll see:

```
Service [mindbridge] revision [mindbridge-00001-xxx] has been deployed
Service URL: https://mindbridge-xxxxx-uc.a.run.app
```

### Test the deployment:

```bash
# Health check
curl https://your-service-url.run.app/health

# API info
curl https://your-service-url.run.app/api
```

---

## Step 6: Configure Custom Domain (Optional)

### Map custom domain:

```bash
# Map domain
gcloud run domain-mappings create \
  --service mindbridge \
  --domain mindbridge-app.run.app \
  --region us-central1

# Verify DNS records
gcloud run domain-mappings describe \
  --domain mindbridge-app.run.app \
  --region us-central1
```

---

## Step 7: Set Up Continuous Deployment

### Connect GitHub Repository:

1. Go to Cloud Console → Cloud Run
2. Click on your service
3. Go to "Set up Continuous Deployment"
4. Connect GitHub repo: `SAMK-online/MindBridge-ClaudRunHack`
5. Select branch: `main`
6. Configure build: Use `Dockerfile` or `cloudbuild.yaml`

---

## Deployment Configuration Details

### Recommended Settings:

| Setting | Value | Reason |
|---------|-------|--------|
| **Memory** | 2Gi | Handles multiple Gemini API calls |
| **CPU** | 2 vCPU | Supports concurrent requests |
| **Timeout** | 300s | Allows for longer conversations |
| **Min Instances** | 0 | Cost-effective (scales to zero) |
| **Max Instances** | 10 | Handles traffic spikes |
| **Concurrency** | 80 | Optimal for FastAPI |
| **Region** | us-central1 | Close to Gemini API |

### Environment Variables:

```yaml
GOOGLE_API_KEY: your_gemini_api_key
GOOGLE_CLOUD_PROJECT: nimacareai
PORT: 8080
ALLOWED_ORIGINS: https://mindbridge-app.run.app
```

---

## Cost Estimation

### Cloud Run Pricing (us-central1):

**Free Tier (per month):**
- 2 million requests
- 360,000 GB-seconds
- 180,000 vCPU-seconds

**Your Configuration (2GB RAM, 2 vCPU):**
- ~$0.04 per 1000 requests
- Estimated: **$5-15/month** for moderate usage
- **Scales to $0** when not in use!

### Cost Optimization Tips:

1. ✅ **Use Min Instances = 0** (scales to zero)
2. ✅ **Set appropriate timeout** (avoid long-running requests)
3. ✅ **Use caching** (reduce Gemini API calls)
4. ✅ **Monitor usage** (Cloud Console)

---

## Monitoring & Logs

### View Logs:

```bash
# Stream logs
gcloud run services logs read mindbridge \
  --region us-central1 \
  --limit 50 \
  --follow

# View in console
gcloud run services describe mindbridge --region us-central1
```

### Access Cloud Console:

1. Go to: https://console.cloud.google.com/run
2. Select project: `nimacareai`
3. Click on service: `mindbridge`
4. View: Metrics, Logs, Revisions

---

## Troubleshooting

### Issue: "API not enabled"

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Issue: "Permission denied"

```bash
# Grant yourself permissions
gcloud projects add-iam-policy-binding nimacareai \
  --member="user:your-email@gmail.com" \
  --role="roles/run.admin"
```

### Issue: "Out of memory"

Increase memory allocation:
```bash
gcloud run services update mindbridge \
  --memory 4Gi \
  --region us-central1
```

### Issue: "Cold start slow"

Set minimum instances:
```bash
gcloud run services update mindbridge \
  --min-instances 1 \
  --region us-central1
```

### Issue: "CORS errors"

Update allowed origins:
```bash
gcloud run services update mindbridge \
  --set-env-vars ALLOWED_ORIGINS="https://your-domain.com,http://localhost:8080" \
  --region us-central1
```

---

## Security Best Practices

### 1. Use Secret Manager (Recommended)

Instead of environment variables:

```bash
# Create secret
echo -n "your_api_key" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Grant access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secret
gcloud run deploy mindbridge \
  --set-secrets=GOOGLE_API_KEY=gemini-api-key:latest \
  --region us-central1
```

### 2. Enable Security Features

```bash
# Force HTTPS
gcloud run services update mindbridge \
  --ingress all \
  --region us-central1

# Add security headers (handled in app)
# See main.py for CORS configuration
```

### 3. Set Up Alerts

Create alerts for:
- High CPU usage
- Memory exhaustion
- Error rates
- Request latency

---

## Updating Your Deployment

### Deploy New Version:

```bash
# Simple update (auto-builds from source)
gcloud run deploy mindbridge \
  --source . \
  --region us-central1

# Or push to GitHub (if CD is set up)
git push origin main
```

### Rollback to Previous Version:

```bash
# List revisions
gcloud run revisions list \
  --service mindbridge \
  --region us-central1

# Rollback
gcloud run services update-traffic mindbridge \
  --to-revisions=mindbridge-00001-xxx=100 \
  --region us-central1
```

---

## Post-Deployment Checklist

After successful deployment:

- [ ] Test all endpoints (`/health`, `/api`, `/chat`)
- [ ] Verify voice interface works
- [ ] Check analytics dashboard
- [ ] Test error handling
- [ ] Verify CORS settings
- [ ] Monitor initial logs
- [ ] Set up Cloud Monitoring alerts
- [ ] Document your service URL
- [ ] Update GitHub README with live URL
- [ ] Test from multiple devices

---

## Quick Commands Reference

```bash
# Deploy
gcloud run deploy mindbridge --source . --region us-central1

# View logs
gcloud run services logs read mindbridge --region us-central1 --follow

# Describe service
gcloud run services describe mindbridge --region us-central1

# Update environment variable
gcloud run services update mindbridge \
  --set-env-vars NEW_VAR=value \
  --region us-central1

# Delete service
gcloud run services delete mindbridge --region us-central1

# List all services
gcloud run services list
```

---

## Service URLs

After deployment, your app will be available at:

- **Service URL**: `https://mindbridge-xxxxx-uc.a.run.app`
- **Landing Page**: `https://your-url.run.app/`
- **Voice Interface**: `https://your-url.run.app/app`
- **Text Chat**: `https://your-url.run.app/chat-ui`
- **API Docs**: `https://your-url.run.app/docs` (FastAPI auto-generated)

---

## Next Steps After Deployment

1. ✅ **Test the live deployment**
2. ✅ **Update GitHub README** with live URL
3. ✅ **Create demo video** using live URL
4. ✅ **Submit to hackathon** with:
   - GitHub repo
   - Live Cloud Run URL
   - Demo video
   - Architecture diagram

---

## Support & Resources

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Gemini API**: https://ai.google.dev/
- **FastAPI on Cloud Run**: https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service
- **Troubleshooting**: https://cloud.google.com/run/docs/troubleshooting

---

**🎉 Ready to deploy? Run the commands above and your multi-agent AI will be live in minutes!** 🚀

---

_For hackathon submission support, see `HACKATHON_SUBMISSION.md`_

