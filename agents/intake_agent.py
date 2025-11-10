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

    Powered by: Gemini 2.0 Flash (Thinking Mode)
    Purpose: Create safe space for users to share at their own pace
    Enhanced empathy and emotional understanding
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
            model_name="gemini-2.5-pro",  # Pro for better conversation flow and reasoning
            temperature=0.85,  # Warm and empathetic
            max_tokens=400  # Increased for deeper conversations
        )

    def get_system_prompt(self) -> str:
        """System prompt for friendly, calming conversation."""
        return """You are Nima, a warm and empathetic wellness support assistant from MindBridge.

Your role: Have a deep, meaningful conversation to truly understand what the user is experiencing.

Therapeutic Approach:
- Reflect back what you hear to show you're listening carefully
- Validate their feelings and normalize their experiences
- Ask thoughtful follow-up questions that go deeper
- Create a safe space where they feel truly heard
- Use 3-4 sentences to fully express empathy and understanding
- Reference specific things they've shared to show you remember

Example good responses:
- "It sounds like you're carrying a lot of weight right now with work pressures. When you say you feel burned out, what does that look like in your day-to-day? Are you finding it hard to feel motivated, or is it more about feeling exhausted?"
- "I hear that career uncertainty is weighing on you. It's completely understandable to feel lost when you're questioning your path. What aspects of your career feel most unsettling right now?"

After 3-4 meaningful exchanges, naturally offer to connect them with a professional counselor who specializes in their area of concern.

Remember: Go deep, not surface level. Each response should build on what they've shared."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Process conversation through warm intake stages.
        """
        print(f"🤝 {self.agent_name} processing...")

        # Check if already complete - don't process again
        if state.agent_data.get("intake_complete"):
            print("✅ Intake already complete - skipping")
            return state

        # Get current stage
        current_stage = state.agent_data.get("intake_stage", self.STAGE_GREETING)

        # Track failed generations to auto-progress
        failed_count = state.agent_data.get("intake_failed_count", 0)

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
        
        # Check if user has agreed to counselor matching
        last_message = self.get_last_user_message(state) or ""
        user_agreed = any(word in last_message.lower() for word in ["yes", "absolutely", "sure", "ok", "okay", "please", "that would be helpful", "yep", "yeah", "connect"])

        # Check if we've asked about counselor matching in the last 3 messages
        asked_about_matching = False
        messages_to_check = min(3, len(state.messages))
        for msg in state.messages[-messages_to_check:]:
            if msg.role == "assistant":
                msg_lower = msg.content.lower()
                if any(phrase in msg_lower for phrase in [
                    "would you like me to match",
                    "connecting with a professional counselor",
                    "match you with someone",
                    "counselor could really help",
                    "connect you with",
                    "find the best match"
                ]):
                    asked_about_matching = True
                    break

        print(f"🔍 User message: '{last_message[:50]}'")
        print(f"🔍 Asked about matching: {asked_about_matching}, User agreed: {user_agreed}")

        # If we asked about matching and user agreed, complete immediately!
        if asked_about_matching and user_agreed and turn_count >= 2:
            print("✅ User agreed to matching - completing intake immediately")
            state.agent_data["intake_complete"] = True
            state.agent_data["intake_stage"] = self.STAGE_READY
            # Don't add another message - let Crisis Agent take over
            return state

        # Build context based on stage - encourage deeper conversations
        if turn_count >= 6 or (turn_count >= 4 and user_agreed):
            context = "The user has agreed to counselor matching. Confirm briefly (ONE sentence only) that you'll connect them with a professional counselor."
            next_stage = self.STAGE_READY
        elif turn_count >= 4:
            context = "Go deeper into their experience. Ask about how this is affecting their daily life, relationships, or well-being. Show that you're really listening by referencing specific details they've shared."
            next_stage = self.STAGE_EXPLORE
        elif turn_count >= 3:
            context = "Continue exploring their concerns with empathy. Ask follow-up questions that show genuine curiosity about their situation. Help them feel heard and understood."
            next_stage = self.STAGE_EXPLORE
        elif turn_count >= 2:
            context = "They've shared something about what brings them here. Reflect back what you heard and ask them to tell you more. Show empathy and validate their feelings."
            next_stage = self.STAGE_EXPLORE
        else:
            context = "This is your first message. Greet them warmly as Nima. Let them know you're here to listen. Ask how they're feeling and what brings them here today."
            next_stage = self.STAGE_CHECK_IN

        # Generate response
        response_text = self.generate_response(state, context)

        # Check if this was a fallback response (indicates AI filter block)
        is_fallback = response_text.startswith("Thank you for sharing") or \
                      response_text.startswith("I appreciate you") or \
                      response_text.startswith("That sounds really") or \
                      response_text.startswith("I hear you") or \
                      response_text.startswith("It takes courage")

        if is_fallback:
            failed_count += 1
            state.agent_data["intake_failed_count"] = failed_count
            print(f"⚠️  AI filter blocked response ({failed_count}/3)")

            # Auto-complete intake after 3 failed attempts
            if failed_count >= 3:
                print("⏭️  Auto-completing intake due to AI filters")
                response_text = "It takes courage to reach out. I'd like to connect you with a professional counselor who can provide the support you need. Let me find someone who's a good match for you."
                state.agent_data["intake_complete"] = True
                next_stage = self.STAGE_READY

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
