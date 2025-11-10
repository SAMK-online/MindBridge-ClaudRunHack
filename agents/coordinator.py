"""
Coordinator Agent - Multi-Agent Orchestration
============================================

This agent orchestrates the workflow between all agents:
1. Routes user to appropriate agent
2. Manages agent transitions
3. Maintains conversation flow
4. Ensures smooth handoffs

Powered by: Gemini 2.0 Flash thinking mode (complex decision-making)
"""

from typing import Optional
from .base_agent import BaseAgent, AgentState
from .intake_agent import IntakeAgent
from .crisis_agent import CrisisAgent
from .resource_agent import ResourceAgent
from .habit_agent import HabitAgent


class CoordinatorAgent(BaseAgent):
    """
    Coordinator that manages the multi-agent workflow.

    Workflow:
    1. Intake Agent - Warm onboarding
    2. Crisis Agent - Risk assessment
    3. Resource Agent - Therapist matching (if needed)
    4. Habit Agent - Habit recommendations
    """

    def __init__(self):
        super().__init__(
            agent_name="Coordinator",
            model_name="gemini-2.0-flash-thinking-exp-1219",  # Thinking mode for orchestration logic
            temperature=0.3,  # Low temp for consistent routing
            max_tokens=200
        )

        # Initialize all agents
        self.intake_agent = IntakeAgent()
        self.crisis_agent = CrisisAgent()
        self.resource_agent = ResourceAgent()
        self.habit_agent = HabitAgent()

    def get_system_prompt(self) -> str:
        """System prompt for coordination"""
        return """You are the Coordinator AI managing NimaCare's multi-agent system.

Your job: Route users through the appropriate workflow:
1. Intake → gather context
2. Crisis → assess risk
3. Resource → match therapist (if needed)
4. Habit → recommend habits

Make intelligent routing decisions based on conversation state."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Orchestrate the multi-agent workflow.
        """
        print("\n" + "="*60)
        print("🎯 COORDINATOR: Determining next agent...")
        print("="*60)

        # Determine which agent should handle next
        next_agent = self._determine_next_agent(state)

        print(f"➡️  Routing to: {next_agent}")

        # Route to appropriate agent
        if next_agent == "intake":
            state.current_agent = "intake"
            state = await self.intake_agent.process(state)

        elif next_agent == "crisis":
            state.current_agent = "crisis"
            state = await self.crisis_agent.process(state)

        elif next_agent == "resource":
            state.current_agent = "resource"
            state = await self.resource_agent.process(state)

        elif next_agent == "habit":
            state.current_agent = "habit"
            state = await self.habit_agent.process(state)

        elif next_agent == "complete":
            # Workflow complete
            final_message = self._generate_completion_message(state)
            state = self.add_message(state, "assistant", final_message)
            state.agent_data["workflow_complete"] = True

        return state

    def _determine_next_agent(self, state: AgentState) -> str:
        """
        Determine which agent should process next based on state.
        """
        # Check workflow flags
        intake_complete = state.agent_data.get("intake_complete", False)
        crisis_complete = state.agent_data.get("crisis_complete", False)
        resource_complete = state.agent_data.get("resource_complete", False)
        habit_complete = state.agent_data.get("habit_complete", False)

        # Sequential workflow
        if not intake_complete:
            return "intake"

        if not crisis_complete:
            return "crisis"

        # Check if therapist matching is needed
        needs_therapist = state.agent_data.get("needs_therapist", False)
        if needs_therapist and not resource_complete:
            return "resource"

        # Offer habit recommendations
        if not habit_complete:
            return "habit"

        # All done
        return "complete"

    def _generate_completion_message(self, state: AgentState) -> str:
        """
        Generate final message when workflow is complete.
        """
        matched = state.agent_data.get("therapist_match_found", False)
        has_habits = len(state.agent_data.get("recommended_habits", [])) > 0

        message = "You've taken an important step today. "

        if matched:
            message += "I've connected you with a therapist who's ready to help. "

        if has_habits:
            message += "Start with those small habits we discussed - they can make a real difference. "

        message += "Remember, you don't have to face this alone."

        return message
