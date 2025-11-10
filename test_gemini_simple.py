#!/usr/bin/env python3
"""
Simple test script to verify Gemini API connection using REST API
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connection using REST"""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        return False

    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ Project ID: {os.getenv('GOOGLE_CLOUD_PROJECT')}")

    # Test with Gemini 1.5 Flash using REST API (stable model)
    print("\n🧪 Testing Gemini 1.5 Flash (REST API)...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [{
            "parts": [{
                "text": "Say 'Hello from NimaCare!' in exactly 5 words."
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)

        # Print the full response for debugging
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        response.raise_for_status()

        result = response.json()
        if "candidates" in result and len(result["candidates"]) > 0:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print(f"✅ Gemini Response: {text.strip()}")
            print("\n✨ SUCCESS! Gemini API is working!")
            return True
        else:
            print(f"❌ Unexpected response: {result}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    exit(0 if success else 1)
