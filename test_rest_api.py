#!/usr/bin/env python3
"""
Test using Gemini REST API directly instead of SDK
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

# Gemini REST API endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

# Request payload
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

print("📡 Sending REST API request...")

try:
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()

    result = response.json()
    text = result['candidates'][0]['content']['parts'][0]['text']

    print(f"✅ Success! Response: {text}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Response: {response.text if 'response' in locals() else 'No response'}")
