#!/usr/bin/env python3
"""
Test script to verify Gemini API connection
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connection"""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        return False

    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ Project ID: {os.getenv('GOOGLE_CLOUD_PROJECT')}")

    try:
        import google.generativeai as genai

        # Configure the API
        genai.configure(api_key=api_key)

        # Test with Gemini 2.5 Flash
        print("\n🧪 Testing Gemini 2.5 Flash...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say 'Hello from NimaCare!' in exactly 3 words.")

        print(f"✅ Gemini 2.5 Flash Response: {response.text}")

        # Test with Gemini 2.5 Pro
        print("\n🧪 Testing Gemini 2.5 Pro...")
        model_pro = genai.GenerativeModel('gemini-2.5-pro')
        response_pro = model_pro.generate_content("Say 'NimaCare ready!' in exactly 3 words.")

        print(f"✅ Gemini 2.5 Pro Response: {response_pro.text}")

        print("\n✨ SUCCESS! Both models are working!")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    exit(0 if success else 1)
