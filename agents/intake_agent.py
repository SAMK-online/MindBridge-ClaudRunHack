"""
Intake Agent - Empathetic Conversational Onboarding
==================================================

This agent provides a warm, gradual introduction to the platform.

KEY PRINCIPLES:
- Warm and friendly tone
- No rushing - max 5 turns before offering help
- Active listening
- Validation of feelings
- Gradual information gathering
"""

from typing import Optional
from .base_agent import BaseAgent, AgentState


class IntakeAgent(BaseAgent):
    """
    Intake Agent for warm, conversational onboarding.

    Powered by: Gemini 1.5 Flash
    Purpose: Create safe space for users to share at their own pace
    """

    # Conversation stages
    STAGE_GREETING = "greeting"
    STAGE_CHECK_IN = "check_in"
    STAGE_EXPLORE = "explore"
    STAGE_READY = "ready_for_assessment"

    # Crisis keywords for immediate escalation
    CRISIS_KEYWORDS = {
        "kill myself", "end it all", "suicide", "hurt myself",
        "take my life", "die", "overdose", "can't go on"
    }

    def __init__(self):
        super().__init__(
            agent_name="Nima (Intake)",
            model_name="gemini-1.5-flash",
            temperature=0.85,  # Warm and empathetic
            max_tokens=250
        )

    def get_system_prompt(self) -> str:
        """System prompt for friendly, calming conversation."""
        return """You are Nima, a warm and empathetic mental health support AI from NimaCare.

Your role: Have a natural conversation to understand what's troubling the user.

Rules:
- Keep responses to 2 sentences maximum
- Be warm, caring, and human-like
- Ask thoughtful questions to understand their situation
- NEVER repeat yourself - each response must be different
- Show empathy and validate their feelings
- After 3-4 exchanges, naturally offer to connect them with a volunteer therapist

Remember: You're here to listen and understand, not to diagnose or give advice."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Process conversation through warm intake stages.
        """
        print(f"🤝 {self.agent_name} processing...")

        # Get current stage
        current_stage = state.agent_data.get("intake_stage", self.STAGE_GREETING)

        # Check for crisis keywords
        last_message = self.get_last_user_message(state)
        if last_message and self._contains_crisis_language(last_message):
            print("🚨 Crisis language detected!")
            response = (
                "Thank you for trusting me. Your safety is the most important thing. "
                "Please call 988 (Suicide & Crisis Lifeline) right now if you're in immediate danger. "
                "I'm connecting you with our crisis specialist to make sure you get the support you need."
            )
            state = self.add_message(state, "assistant", response)
            state.agent_data["intake_complete"] = True
            state.agent_data["force_crisis"] = True
            return state

        # Determine conversation progress
        turn_count = len([m for m in state.messages if m.role == "user"])

        # Build context based on stage
        if turn_count >= 5:
            context = "The user has shared enough. Warmly offer to connect them with a volunteer therapist."
            next_stage = self.STAGE_READY
        elif turn_count >= 3:
            context = "Continue exploring their concerns with empathy."
            next_stage = self.STAGE_EXPLORE
        elif turn_count >= 2:
            context = "Ask what brought them here today."
            next_stage = self.STAGE_EXPLORE
        else:
            context = "Greet them warmly and ask how they're feeling."
            next_stage = self.STAGE_CHECK_IN

        # Generate response
        response_text = self.generate_response(state, context)

        # Add response to state
        state = self.add_message(state, "assistant", response_text)

        # Update stage
        state.agent_data["intake_stage"] = next_stage

        # Mark as complete if ready for assessment
        if next_stage == self.STAGE_READY:
            state.agent_data["intake_complete"] = True
            print("✅ Intake complete - ready for crisis assessment")

        return state

    def _contains_crisis_language(self, text: str) -> bool:
        """Check if message contains crisis keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.CRISIS_KEYWORDS)
