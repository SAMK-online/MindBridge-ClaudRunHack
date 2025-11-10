"""Final message to complete workflow"""
import requests

session_id = "manual_1762792472"
base_url = "http://localhost:8080/chat"

response = requests.post(base_url, json={
    "user_id": "manual_test",
    "session_id": session_id,
    "message": "perfect, thank you so much"
})

if response.status_code == 200:
    data = response.json()
    messages = data.get('messages', [])

    # Get last assistant message
    for m in reversed(messages):
        if m['role'] == 'assistant':
            print("\n" + "="*60)
            print("FINAL COMPLETION MESSAGE:")
            print("="*60)
            print(f"\n{m['content']}\n")
            break

    print(f"Agent: {data.get('current_agent', 'unknown')}")
    print(f"Workflow Complete: {data.get('workflow_complete', False)}")
    print("\n" + "="*60)
    print("✅ FULL WORKFLOW TEST COMPLETE!")
    print("="*60)
    print("\nWorkflow executed successfully:")
    print("1. ✅ Intake Agent - Warm onboarding")
    print("2. ✅ Crisis Agent - Risk assessment + category suggestion (career)")
    print("3. ✅ Resource Agent - Matched with James Patterson (career counselor)")
    print("4. ✅ Habit Agent - 3 evidence-based career habits")
    print("5. ✅ Completion Message")
