#!/usr/bin/env python3
"""
Test if the API key works at all by listing models
"""
import os
import requests

# Load API key from .env
with open(".env") as f:
    for line in f:
        if line.startswith("GOOGLE_API_KEY="):
            api_key = line.strip().split("=", 1)[1]
            break

print(f"🔑 Using API key: {api_key[:20]}...")
print("\n📋 Attempting to list available models...")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        result = response.json()
        models = result.get('models', [])

        print(f"\n✅ API KEY WORKS! Found {len(models)} models:")
        for model in models[:10]:  # Show first 10
            name = model.get('name', '').replace('models/', '')
            print(f"   - {name}")

        if len(models) > 10:
            print(f"   ... and {len(models) - 10} more models")

    elif response.status_code == 403:
        print("\n❌ 403 FORBIDDEN")
        print("The API key doesn't have permission to access Generative Language API")
        print("\nTo fix:")
        print("1. Go to https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
        print("2. Select project 'nimacareai'")
        print("3. Click 'Enable' button")
        print("4. Wait 1-2 minutes for changes to propagate")
    else:
        print(f"\n❌ HTTP {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"\n❌ Error: {e}")
