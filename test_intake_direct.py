"""
Test Intake Agent directly
"""
import asyncio
import os
from dotenv import load_dotenv
from agents.intake_agent import IntakeAgent
from agents.base_agent import AgentState, AgentMessage

# Load environment
load_dotenv()

async def test_intake():
    agent = IntakeAgent()

    print(f"Agent Name: {agent.agent_name}")
    print(f"Model Name: {agent.model_name}")
    print(f"Temperature: {agent.temperature}")
    print()

    # Create state
    state = AgentState(
        messages=[AgentMessage(role="user", content="Hello")],
        agent_data={},
        user_id="test_user"
    )

    print("Processing...")
    result = await agent.process(state)

    print("\nResult:")
    for msg in result.messages:
        print(f"{msg.role}: {msg.content}")

if __name__ == "__main__":
    asyncio.run(test_intake())
