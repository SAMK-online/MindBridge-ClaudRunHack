#!/usr/bin/env python3
"""
Test script to list available models and verify API access
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")

# Try to list available models
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print(f"\n🔍 Trying to list available models...")
print(f"URL: {url[:80]}...")

response = requests.get(url, timeout=30)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    print("\n✅ Available models:")
    for model in data.get('models', [])[:5]:
        print(f"  - {model.get('name', 'Unknown')}")
else:
    print(f"\n❌ Failed to list models")
