#!/usr/bin/env python3
"""
Test with all available Gemini model names to find which ones work
"""
import os
import requests
import json

# Load API key from .env manually
with open(".env") as f:
    for line in f:
        if line.startswith("GOOGLE_API_KEY="):
            api_key = line.strip().split("=", 1)[1]
            break

print(f"🔑 Using API key: {api_key[:20]}...")

# Test with all known Gemini model variants
models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-2.0-flash-exp",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-pro",
]

working_models = []

for model_name in models_to_test:
    print(f"\n📡 Testing model: {model_name}")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [{
                "text": "Say 'Hello from NimaCare!' in one short sentence."
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 50
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ SUCCESS! Response: {text}")
            working_models.append(model_name)
        else:
            print(f"❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*60)
if working_models:
    print(f"✅ WORKING MODELS ({len(working_models)}):")
    for model in working_models:
        print(f"   - {model}")
else:
    print("❌ NO MODELS WORKING - API key may not have permissions")
