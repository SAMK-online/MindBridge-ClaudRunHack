"""
Simple test to verify Gemini API is working
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key (first 10 chars): {api_key[:10]}...")

genai.configure(api_key=api_key)

# Test 1: Simple prompt with Flash
print("\n=== Test 1: Gemini 2.5 Flash ===")
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Say hello in a friendly way")
    print(f"✅ Success: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Simple prompt with Pro
print("\n=== Test 2: Gemini 2.5 Pro ===")
try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content("Say hello in a friendly way")
    print(f"✅ Success: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: With safety settings
print("\n=== Test 3: With Safety Settings ===")
try:
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    model = genai.GenerativeModel('gemini-2.5-flash')

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    response = model.generate_content(
        "Say hello in a friendly way",
        safety_settings=safety_settings
    )
    print(f"✅ Success: {response.text}")
    print(f"Finish reason: {response.candidates[0].finish_reason}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Wellness conversation
print("\n=== Test 4: Wellness Conversation ===")
try:
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    model = genai.GenerativeModel('gemini-2.5-flash')

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    prompt = """You are a friendly wellness assistant.
    A user says: "I want to talk to someone"
    Respond warmly in 1-2 sentences."""

    response = model.generate_content(
        prompt,
        safety_settings=safety_settings
    )

    print(f"Response candidates: {len(response.candidates)}")
    if response.candidates:
        candidate = response.candidates[0]
        print(f"Finish reason: {candidate.finish_reason}")
        print(f"Safety ratings: {candidate.safety_ratings}")

        if candidate.content and candidate.content.parts:
            print(f"✅ Success: {response.text}")
        else:
            print(f"❌ Content blocked even with BLOCK_NONE")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== Tests Complete ===")
