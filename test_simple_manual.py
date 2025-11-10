"""Simple manual test to validate full workflow"""
import requests
import json
import time

session_id = f"manual_{int(time.time())}"
base_url = "http://localhost:8080/chat"

def send_message(msg):
    """Send message and print last response"""
    print(f"\n{'='*60}")
    print(f"USER: {msg}")
    print('='*60)

    response = requests.post(base_url, json={
        "user_id": "manual_test",
        "session_id": session_id,
        "message": msg
    })

    if response.status_code == 200:
        data = response.json()
        messages = data.get('messages', [])

        # Get last assistant message
        for m in reversed(messages):
            if m['role'] == 'assistant':
                print(f"\nASSISTANT ({data['current_agent']}): {m['content'][:200]}...")
                break

        print(f"\nAgent: {data['current_agent']}")
        print(f"Complete: {data.get('workflow_complete', False)}")

        # Print habits if present in agent_data (won't be in response but will show in logs)
        return data
    else:
        print(f"ERROR: {response.status_code}")
        return None

# Test conversation
print("🧪 TESTING FULL WORKFLOW WITH HABIT AGENT\n")
print(f"Session: {session_id}\n")

send_message("hi")
time.sleep(2)

send_message("I'm burned out at work and need career guidance")
time.sleep(2)

send_message("yes, I want help with my career")
time.sleep(2)

send_message("connect me with a career counselor")
time.sleep(2)

send_message("yes, career specialist sounds perfect")
time.sleep(2)

print("\n" + "="*60)
print("✅ TEST COMPLETE - Check server logs for full agent flow")
print("="*60)
