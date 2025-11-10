## NimaCare API Troubleshooting Checklist

Current Issue: All API keys return 403 Forbidden

### ✅ Things to Verify:

#### 1. Billing Account (CRITICAL)
- Go to: https://console.cloud.google.com/billing?project=nimacareai
- Verify that the project has an active billing account linked
- ⚠️ Gemini API requires billing to be enabled, even though there's a free tier

#### 2. Generative Language API Status
- Go to: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/metrics?project=nimacareai
- Should say "API enabled" at the top
- If not, enable it here: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com?project=nimacareai

#### 3. API Key Restrictions
- Go to: https://console.cloud.google.com/apis/credentials?project=nimacareai
- Click on your API key
- Check "API restrictions":
  ✅ Should be "Don't restrict key" OR
  ✅ Should include "Generative Language API" in allowed APIs
- Check "Application restrictions":
  ✅ Should be "None" (for testing)

#### 4. Create New Unrestricted Key (Recommended)
- Go to: https://console.cloud.google.com/apis/credentials?project=nimacareai
- Click "+ CREATE CREDENTIALS" → "API Key"
- Click "EDIT API KEY" on the new key
- Set API restrictions to "Don't restrict key"
- Set Application restrictions to "None"
- Click "Save"
- Copy the new key

#### 5. Alternative: Use AI Studio
- Go to: https://aistudio.google.com/app/apikey
- Make sure you're signed in with the same Google account
- Create an API key there
- AI Studio keys often have fewer restrictions

---

### 🎯 Next Steps:

1. **If billing is not enabled**: Enable billing first
2. **If API is not enabled**: Enable Generative Language API
3. **If key has restrictions**: Remove restrictions or create new key
4. Share the new unrestricted API key with me

The most common issue is **missing billing** - even though Gemini has a free tier, the project must have billing enabled to use it.
