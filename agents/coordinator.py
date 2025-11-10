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
            model_name="gemini-2.5-pro",  # Pro model for orchestration logic
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

        Flow: Intake → Crisis (with category suggestion) → Resource (filtered) → Habit → Complete
        """
        # Check workflow flags
        intake_complete = state.agent_data.get("intake_complete", False)
        crisis_complete = state.agent_data.get("crisis_complete", False)
        resource_complete = state.agent_data.get("resource_complete", False)
        habit_complete = state.agent_data.get("habit_complete", False)

        # Sequential workflow: Intake → Crisis → Resource → Habit → Complete
        if not intake_complete:
            return "intake"

        if not crisis_complete:
            return "crisis"

        # After crisis assessment, show counselor options
        # (Crisis agent suggests a category, Resource agent filters by it)
        if not resource_complete:
            return "resource"

        # After counselor matching, provide habit recommendations
        # (Habit agent recommends habits based on selected category)
        if not habit_complete:
            return "habit"

        # All done - user has counselors and habits
        return "complete"

    def _generate_completion_message(self, state: AgentState) -> str:
        """
        Generate final message when workflow is complete.
        """
        matched = state.agent_data.get("therapist_match_found", False)
        selected_category = state.agent_data.get("selected_category") or \
                          state.agent_data.get("suggested_category", "general")
        habits_recommended = state.agent_data.get("habit_complete", False)

        message = "You've taken an important step today by reaching out. "

        if matched:
            message += f"I've connected you with {selected_category} counselors who are ready to help you. "
            message += "Feel free to reach out to any of them to get started. "
        else:
            message += "We're here to support you in finding the right counselor. "

        if habits_recommended:
            message += "In the meantime, the habits I've shared can help you start making progress right away. "

        message += "\n\nRemember, you don't have to face this alone. "
        message += "Take care, and reach out whenever you need support. 💙"

        return message
