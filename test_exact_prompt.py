"""
Test the exact prompt that's failing in the intake agent
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Load environment
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# The exact prompt that's being used
system_prompt = """You are Nima, a warm and empathetic wellness support assistant from NimaCare.

Your role: Have a natural, supportive conversation to understand what the user would like help with.

Rules:
- Keep responses to 2 sentences maximum
- Be warm, caring, and conversational
- Ask thoughtful questions to understand their situation
- NEVER repeat yourself - each response must be different
- Show empathy and validate their feelings
- After 3-4 exchanges, naturally offer to connect them with a professional counselor

Remember: You're here to listen and understand."""

context = "Greet them warmly and ask how they're feeling."

conversation_history = "user: Hello"

full_prompt = f"""{system_prompt}

{context}

Conversation history:
{conversation_history}

Respond as the assistant (keep it concise, 2-3 sentences):"""

print("Testing with Gemini 2.5 Pro...")
print(f"Prompt length: {len(full_prompt)} chars")
print()

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    response = model.generate_content(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.85,
            max_output_tokens=250,
        ),
        safety_settings=safety_settings
    )

    print(f"Candidates: {len(response.candidates)}")
    if response.candidates:
        candidate = response.candidates[0]
        print(f"Finish reason: {candidate.finish_reason}")
        print(f"Safety ratings: {candidate.safety_ratings}")

        if candidate.content and candidate.content.parts:
            print(f"\n✅ Success!")
            print(f"Response: {response.text}")
        else:
            print(f"\n❌ Content blocked!")
            print(f"Full candidate: {candidate}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*60)
print("Now testing with Flash instead of Pro...")
print("="*60 + "\n")

try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.85,
            max_output_tokens=250,
        ),
        safety_settings=safety_settings
    )

    print(f"Candidates: {len(response.candidates)}")
    if response.candidates:
        candidate = response.candidates[0]
        print(f"Finish reason: {candidate.finish_reason}")
        print(f"Safety ratings: {candidate.safety_ratings}")

        if candidate.content and candidate.content.parts:
            print(f"\n✅ Success!")
            print(f"Response: {response.text}")
        else:
            print(f"\n❌ Content blocked!")
except Exception as e:
    print(f"❌ Exception: {e}")
