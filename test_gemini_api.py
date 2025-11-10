#!/usr/bin/env python3
"""
Quick test to see if Gemini API works with API key
"""
import os
import google.generativeai as genai

# Remove service account env var if it exists
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

# Load API key from .env manually
with open(".env") as f:
    for line in f:
        if line.startswith("GOOGLE_API_KEY="):
            api_key = line.strip().split("=", 1)[1]
            break

print(f"🔑 Using API key: {api_key[:20]}...")

# Configure Gemini
genai.configure(api_key=api_key)

# Create model
model = genai.GenerativeModel("gemini-2.0-flash-exp")

print("📡 Sending test request...")

# Generate response
try:
    response = model.generate_content(
        "Say 'Hello from NimaCare!' in one short sentence.",
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=50,
        )
    )
    print(f"✅ Success! Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
