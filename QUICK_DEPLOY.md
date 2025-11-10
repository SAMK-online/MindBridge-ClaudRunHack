# ⚡ Quick Deploy Guide - MindBridge to Cloud Run

## 🎯 Deploy in 3 Steps

---

## Step 1️⃣: Install Google Cloud SDK

Choose your platform:

### **macOS** (Recommended: Homebrew)
```bash
brew install --cask google-cloud-sdk
```

Or using curl:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### **Windows**
Download and run installer:
https://cloud.google.com/sdk/docs/install

### **Linux**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

---

## Step 2️⃣: Authenticate

```bash
# Login to Google Cloud
gcloud auth login

# Set project
gcloud config set project nimacareai

# Enable APIs (one-time setup)
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

## Step 3️⃣: Deploy!

### **Option A: Automated Script (Easiest)** ⭐

```bash
cd /Users/abdulshaik/CloudRunHack/MindBridge-ClaudRunHack
./deploy.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Load your API key from `.env`
- ✅ Enable required APIs
- ✅ Deploy to Cloud Run
- ✅ Test the deployment
- ✅ Give you the live URL

### **Option B: Manual Command**

```bash
gcloud run deploy mindbridge \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars GOOGLE_API_KEY="AIzaSyC9jaU5hmQIbSwgAAG75AGONV5XU9WyIOg"
```

---

## 📊 Deployment Details

| Setting | Value | Why |
|---------|-------|-----|
| **Memory** | 2Gi | Handles multiple Gemini calls |
| **CPU** | 2 vCPU | Supports concurrent users |
| **Timeout** | 300s | Long conversations |
| **Region** | us-central1 | Low latency |
| **Cost** | ~$0.04/1000 requests | Scales to $0 when idle |

---

## ✅ After Deployment

You'll see:
```
Service URL: https://mindbridge-xxxxx-uc.a.run.app
```

### **Test Your Deployment:**

1. **Landing Page**: `https://your-url.run.app/`
2. **Voice Interface**: `https://your-url.run.app/app`
3. **Health Check**: `https://your-url.run.app/health`
4. **API Docs**: `https://your-url.run.app/docs`

### **View Logs:**
```bash
gcloud run services logs read mindbridge --region us-central1 --follow
```

---

## 🔧 Troubleshooting

### "gcloud: command not found"
→ Install Google Cloud SDK (Step 1)

### "API not enabled"
```bash
gcloud services enable run.googleapis.com
```

### "Permission denied"
→ Make sure billing is enabled: https://console.cloud.google.com/billing

### "Deployment failed"
```bash
# Check logs
gcloud run services logs read mindbridge --region us-central1

# Try with more verbose output
gcloud run deploy mindbridge --source . --verbosity=debug
```

---

## 🎥 Next: Create Demo Video

After successful deployment:

1. ✅ Visit your live URL
2. ✅ Record 3-minute demo showing:
   - Landing page
   - Voice interface in action
   - Analytics dashboard
   - Agent handoffs
   - Multi-agent collaboration
3. ✅ Submit to hackathon with:
   - GitHub: https://github.com/SAMK-online/MindBridge-ClaudRunHack
   - Live URL: (your Cloud Run URL)
   - Demo video

---

## 📞 Quick Help

**Can't install gcloud?**
→ Use Cloud Console web interface:
1. Go to https://console.cloud.google.com/run
2. Click "Create Service"
3. Select "Deploy from Git"
4. Connect GitHub repo
5. Set environment variables

**Need to update after deployment?**
```bash
./deploy.sh  # Run again to redeploy
```

**Want to rollback?**
```bash
gcloud run revisions list --service mindbridge --region us-central1
gcloud run services update-traffic mindbridge --to-revisions=REVISION_NAME=100
```

---

## 🚀 Ready to Deploy?

```bash
cd /Users/abdulshaik/CloudRunHack/MindBridge-ClaudRunHack
./deploy.sh
```

**That's it! Your multi-agent AI will be live in ~5 minutes!** 🎉

---

_For detailed deployment options, see `DEPLOYMENT_GUIDE.md`_

