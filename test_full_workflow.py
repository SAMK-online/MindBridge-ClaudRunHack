"""
Test Script - Complete Workflow with Habit Agent
================================================

Tests the full multi-agent workflow:
1. Intake Agent - Onboarding
2. Crisis Agent - Assessment + Category Suggestion
3. Resource Agent - Counselor Matching (filtered by category)
4. Habit Agent - Habit Recommendations (based on category)
5. Completion Message

This validates the entire user journey.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def print_separator(title=""):
    print("\n" + "="*60)
    if title:
        print(f" {title}")
        print("="*60)

def chat(session_id: str, message: str):
    """Send a message and get response"""
    print_separator(f"USER: {message}")

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "session_id": session_id,
            "message": message,
            "user_id": "test_user_001"
        }
    )

    if response.status_code == 200:
        data = response.json()

        # Get the last assistant message
        messages = data.get('messages', [])
        last_assistant_msg = None
        for msg in reversed(messages):
            if msg.get('role') == 'assistant':
                last_assistant_msg = msg.get('content', '')
                break

        if last_assistant_msg:
            print(f"\nASSISTANT: {last_assistant_msg}")

        print(f"\nAgent: {data.get('current_agent', 'unknown')}")
        print(f"Workflow Complete: {data.get('workflow_complete', False)}")
        return data
    else:
        print(f"ERROR: {response.status_code}")
        print(response.text)
        return None

def test_career_counseling_with_habits():
    """
    Test career counseling flow with habit recommendations.

    Expected flow:
    1. Intake: User shares career struggles
    2. Crisis: Suggests 'career' category
    3. Resource: Shows career counselors (James Patterson)
    4. Habit: Recommends career-related habits
    5. Complete: Final message
    """
    session_id = f"test_session_{int(time.time())}"

    print_separator("🧪 TEST: Career Counseling with Habits")
    print(f"Session ID: {session_id}")

    # Step 1: Initial contact
    chat(session_id, "hi, I need help")
    time.sleep(1)

    # Step 2: Share career struggles (trigger intake completion)
    chat(session_id, "I'm struggling at work, feeling unfulfilled and burned out")
    time.sleep(1)

    # Step 3: Continue conversation (may trigger auto-progression)
    chat(session_id, "yes, I want to talk to someone about my career")
    time.sleep(1)

    # Step 4: Accept career counselor category
    result = chat(session_id, "yes, career specialist sounds good")
    time.sleep(1)

    # Check if workflow is complete (should include habits now)
    if result and result.get('workflow_complete'):
        print_separator("✅ WORKFLOW COMPLETE")
        print("\nExpected components:")
        print("- Intake conversation ✓")
        print("- Crisis assessment with category suggestion ✓")
        print("- Resource matching (career counselors) ✓")
        print("- Habit recommendations (career habits) ✓")
        print("- Completion message ✓")
    else:
        print_separator("⚠️  Workflow not complete yet")
        # Send one more message to progress
        chat(session_id, "thank you")

def test_anxiety_counseling_with_habits():
    """
    Test anxiety counseling flow with habit recommendations.
    """
    session_id = f"test_session_{int(time.time())}"

    print_separator("🧪 TEST: Anxiety Counseling with Habits")
    print(f"Session ID: {session_id}")

    # Step 1: Initial contact
    chat(session_id, "hi")
    time.sleep(1)

    # Step 2: Share anxiety issues
    chat(session_id, "I've been having panic attacks and feel anxious all the time")
    time.sleep(1)

    # Step 3: Continue
    chat(session_id, "yes, I need help managing my anxiety")
    time.sleep(1)

    # Step 4: Accept anxiety counselor
    result = chat(session_id, "yes, anxiety specialist please")
    time.sleep(1)

    if result and result.get('workflow_complete'):
        print_separator("✅ WORKFLOW COMPLETE")
    else:
        chat(session_id, "sounds good")

if __name__ == "__main__":
    print("\n" + "🚀 NIMACARE - FULL WORKFLOW TEST" + "\n")
    print("Testing complete workflow: Intake → Crisis → Resource → Habit → Complete\n")

    try:
        # Test 1: Career counseling
        test_career_counseling_with_habits()

        print("\n\n" + "="*60)
        print("Waiting 3 seconds before next test...")
        print("="*60)
        time.sleep(3)

        # Test 2: Anxiety counseling
        test_anxiety_counseling_with_habits()

        print_separator("🎉 ALL TESTS COMPLETE")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
