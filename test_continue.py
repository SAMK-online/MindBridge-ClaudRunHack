"""Continue the manual test to see Resource and Habit agents"""
import requests
import time

session_id = "manual_1762792472"  # Same session from previous test
base_url = "http://localhost:8080/chat"

def send_message(msg):
    """Send message and print response"""
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
                print(f"\nASSISTANT ({data['current_agent']}): {m['content']}")
                break

        print(f"\nAgent: {data['current_agent']}")
        print(f"Complete: {data.get('workflow_complete', False)}")
        return data
    else:
        print(f"ERROR: {response.status_code}")
        return None

print("🧪 CONTINUING TEST - Accepting career counselor\n")

# Accept the career specialist suggestion
send_message("yes")
time.sleep(2)

# One more message if needed
send_message("sounds great")

print("\n" + "="*60)
print("✅ CHECK SERVER LOGS FOR RESOURCE AND HABIT AGENTS")
print("="*60)
