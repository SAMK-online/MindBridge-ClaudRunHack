# MindBridge - Deployment Guide

**Project:** nimacareai  
**Project Number:** 283246315055  
**Region:** us-central1

---

## 🚀 Quick Deploy to Cloud Run

### Prerequisites
1. ✅ Google Cloud SDK installed
2. ✅ Authenticated to your project
3. ✅ API key configured

---

## Option 1: One-Command Deploy (Recommended)

```bash
# Authenticate
gcloud auth login
gcloud config set project nimacareai

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com

# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

**That's it!** Cloud Build will:
1. Build the Docker image
2. Push to Container Registry
3. Deploy to Cloud Run
4. Set environment variables
5. Configure resources (2GB RAM, 2 CPU)

---

## Option 2: Manual Deployment

### Step 1: Build the Docker image
```bash
docker build -t gcr.io/nimacareai/mindbridge:latest .
```

### Step 2: Push to Container Registry
```bash
docker push gcr.io/nimacareai/mindbridge:latest
```

### Step 3: Deploy to Cloud Run
```bash
gcloud run deploy mindbridge \
  --image gcr.io/nimacareai/mindbridge:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars GOOGLE_API_KEY=AIzaSyC9jaU5hmQIbSwgAAG75AGONV5XU9WyIOg,GOOGLE_CLOUD_PROJECT=nimacareai
```

---

## 🔗 After Deployment

### Get Your URL
```bash
gcloud run services describe mindbridge \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### Expected Output
```
https://mindbridge-xxxxxxxxxx-uc.a.run.app
```

### Update CORS Origins
After deployment, update CORS to allow your Cloud Run URL:

```bash
# Get your deployed URL
CLOUD_RUN_URL=$(gcloud run services describe mindbridge \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

# Update with CORS origins
gcloud run services update mindbridge \
  --region us-central1 \
  --update-env-vars ALLOWED_ORIGINS="${CLOUD_RUN_URL},http://localhost:8080"
```

---

## 🧪 Test Your Deployment

### 1. Health Check
```bash
CLOUD_RUN_URL=$(gcloud run services describe mindbridge \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

curl ${CLOUD_RUN_URL}/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. API Info
```bash
curl ${CLOUD_RUN_URL}/api
```

Expected response:
```json
{
  "service": "NimaCare API",
  "status": "healthy",
  "version": "1.0.0",
  "agents": ["Intake", "Crisis", "Resource", "Habit"]
}
```

### 3. Visit the Voice Interface
```bash
echo "Visit: ${CLOUD_RUN_URL}"
```

Open the URL in your browser and test the voice interface!

---

## 🔐 Environment Variables

The following environment variables are configured:

| Variable | Value | Purpose |
|----------|-------|---------|
| `GOOGLE_API_KEY` | AIzaSy...IOg | Gemini API authentication |
| `GOOGLE_CLOUD_PROJECT` | nimacareai | Project identifier |
| `ALLOWED_ORIGINS` | Auto-configured | CORS security |
| `PORT` | 8080 (default) | Server port |

---

## 📊 Monitor Your Deployment

### View Logs
```bash
gcloud run services logs read mindbridge \
  --region us-central1 \
  --limit 50
```

### Stream Live Logs
```bash
gcloud run services logs tail mindbridge \
  --region us-central1
```

### Check Service Status
```bash
gcloud run services describe mindbridge \
  --region us-central1
```

---

## 🔧 Update Deployment

### Redeploy with Changes
```bash
# After making code changes
gcloud builds submit --config cloudbuild.yaml
```

### Update Environment Variables Only
```bash
gcloud run services update mindbridge \
  --region us-central1 \
  --update-env-vars KEY=VALUE
```

### Scale Resources
```bash
# Increase memory
gcloud run services update mindbridge \
  --region us-central1 \
  --memory 4Gi

# Increase CPU
gcloud run services update mindbridge \
  --region us-central1 \
  --cpu 4
```

---

## 💰 Cost Estimates

**Cloud Run Pricing (us-central1):**
- CPU: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second
- Requests: $0.40/million requests

**Estimated Monthly Cost (Light Usage):**
- ~1,000 requests/month: **< $1**
- ~10,000 requests/month: **$5-10**
- ~100,000 requests/month: **$50-100**

**Free Tier Includes:**
- 2 million requests/month
- 360,000 GiB-seconds/month
- 180,000 vCPU-seconds/month

---

## 🐛 Troubleshooting

### Build Fails
```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds describe BUILD_ID
```

### Service Not Responding
```bash
# Check service status
gcloud run services describe mindbridge --region us-central1

# View recent logs
gcloud run services logs read mindbridge --region us-central1 --limit 100
```

### CORS Errors
```bash
# Update CORS origins
gcloud run services update mindbridge \
  --region us-central1 \
  --update-env-vars ALLOWED_ORIGINS="https://your-domain.com,http://localhost:8080"
```

### Out of Memory
```bash
# Increase memory allocation
gcloud run services update mindbridge \
  --region us-central1 \
  --memory 4Gi
```

---

## 🔒 Security Best Practices

### 1. Use Secret Manager (Recommended)
Instead of environment variables, use Secret Manager for API keys:

```bash
# Create secret
echo -n "AIzaSyC9jaU5hmQIbSwgAAG75AGONV5XU9WyIOg" | \
  gcloud secrets create gemini-api-key --data-file=-

# Update Cloud Run to use secret
gcloud run services update mindbridge \
  --region us-central1 \
  --update-secrets=GOOGLE_API_KEY=gemini-api-key:latest
```

### 2. Enable Authentication (Optional)
To require authentication:

```bash
gcloud run services update mindbridge \
  --region us-central1 \
  --no-allow-unauthenticated
```

### 3. Set Up Custom Domain
```bash
gcloud run domain-mappings create \
  --service mindbridge \
  --domain mindbridge.your-domain.com \
  --region us-central1
```

---

## 🎯 Production Checklist

Before going to production:

- [ ] Move API key to Secret Manager
- [ ] Configure custom domain
- [ ] Set up Cloud CDN
- [ ] Enable Cloud Armor (DDoS protection)
- [ ] Configure monitoring alerts
- [ ] Set up error reporting
- [ ] Configure backup strategy
- [ ] Update CORS to production domains only
- [ ] Enable Cloud Run authentication (if needed)
- [ ] Set up CI/CD with GitHub Actions

---

## 📞 Support Commands

### Delete Service
```bash
gcloud run services delete mindbridge --region us-central1
```

### List All Services
```bash
gcloud run services list --region us-central1
```

### View Service Details
```bash
gcloud run services describe mindbridge \
  --region us-central1 \
  --format yaml
```

---

## 🚀 Your Deployment URLs

**After deployment, your service will be available at:**

```
https://mindbridge-xxxxxxxxxx-uc.a.run.app
```

**Test it:**
1. Visit the URL in your browser
2. Allow microphone access
3. Tap the orb and start speaking!

---

**Project:** nimacareai (283246315055)  
**Region:** us-central1  
**Service:** mindbridge  

Happy deploying! 🎉

