"""
Privacy Agent - Privacy Tier Selection
======================================

This agent helps users choose their privacy level.

Presents 4 options matching the frontend mockup:
1. Full Support - AI stays with you, keeps notes
2. Assisted Handoff - Help connecting with therapist
3. Your Private Notes - High-level notes, user controls details
4. No Records - Totally private, nothing saved

Powered by: Deterministic (no LLM needed)
"""

from typing import Optional
import os
from .base_agent import BaseAgent, AgentState
from models.user import PrivacyTier


class PrivacyAgent(BaseAgent):
    """
    Privacy Agent for privacy tier selection.

    Presents options and captures user's choice.
    Deterministic - no LLM calls needed.
    """

    def __init__(self):
        super().__init__(
            agent_name="Privacy Coordinator",
            model_name="gemini-2.5-flash",  # Model set but not used
            temperature=0.7,
            max_tokens=300
        )

    def get_system_prompt(self) -> str:
        """Not used - deterministic agent"""
        return ""

    async def process(self, state: AgentState) -> AgentState:
        """
        Present privacy options and capture selection.
        Deterministic flow - no LLM needed.
        """
        print(f"🔒 {self.agent_name} presenting privacy options...")

        # Demo mode: Auto-complete
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        if demo_mode and not state.agent_data.get("privacy_complete"):
            print("🎬 DEMO MODE: Auto-selecting Full Support privacy tier")
            selected_tier = PrivacyTier.FULL_SUPPORT.value
            state.agent_data["selected_privacy_tier"] = selected_tier
            state.agent_data["privacy_complete"] = True

            response_text = f"Perfect! I've set your privacy level to **Full Support**. I'll stay with you throughout your journey, keeping helpful notes and reminders."
            state = self.add_message(state, "assistant", response_text)
            return state

        # Check if already asked
        if state.agent_data.get("privacy_presented"):
            # User is responding with their choice
            last_message = self.get_last_user_message(state)
            if last_message:
                selected_tier = self._detect_privacy_choice(last_message)

                if selected_tier:
                    print(f"✅ User selected: {selected_tier}")
                    state.agent_data["selected_privacy_tier"] = selected_tier
                    state.agent_data["privacy_complete"] = True

                    # Confirm selection
                    tier_name = self._get_tier_display_name(selected_tier)
                    response_text = f"Perfect! You've selected **{tier_name}**. Your privacy preferences have been saved."
                    state = self.add_message(state, "assistant", response_text)
                    return state
                else:
                    # Couldn't detect - ask again
                    response_text = "I didn't catch that. Could you please choose one of the privacy levels: Full Support, Assisted Handoff, Your Private Notes, or No Records?"
                    state = self.add_message(state, "assistant", response_text)
                    return state

        # First time - present options
        response_text = self._format_privacy_options()
        state = self.add_message(state, "assistant", response_text)
        state.agent_data["privacy_presented"] = True

        print("✅ Privacy options presented")
        return state

    def _format_privacy_options(self) -> str:
        """Format privacy options for user"""
        return """Thanks for sharing all of that. Which privacy level feels best for you?

**Full Support**
AI can stay with you the whole way, keeping helpful notes and reminders.

**Assisted Handoff**
We'll help connect you to a therapist and smooth the transitions.

**Your Private Notes**
We keep high-level notes while you stay in control of the details.

**No Records**
Totally private—nothing saved, just this conversation.

Pick what feels safest. You can always change your mind later."""

    def _detect_privacy_choice(self, message: str) -> Optional[str]:
        """Detect which privacy tier user selected"""
        message_lower = message.lower()

        # Check for each tier
        if any(word in message_lower for word in ["full support", "full", "maximum support", "all the way"]):
            return PrivacyTier.FULL_SUPPORT.value

        if any(word in message_lower for word in ["assisted handoff", "assisted", "help connect", "transitions"]):
            return PrivacyTier.ASSISTED_HANDOFF.value

        if any(word in message_lower for word in ["private notes", "your private", "high level", "my notes"]):
            return PrivacyTier.YOUR_PRIVATE_NOTES.value

        if any(word in message_lower for word in ["no records", "nothing saved", "totally private", "anonymous"]):
            return PrivacyTier.NO_RECORDS.value

        # Check for numbers (1-4)
        if "1" in message_lower or "first" in message_lower:
            return PrivacyTier.FULL_SUPPORT.value
        if "2" in message_lower or "second" in message_lower:
            return PrivacyTier.ASSISTED_HANDOFF.value
        if "3" in message_lower or "third" in message_lower:
            return PrivacyTier.YOUR_PRIVATE_NOTES.value
        if "4" in message_lower or "fourth" in message_lower:
            return PrivacyTier.NO_RECORDS.value

        return None

    def _get_tier_display_name(self, tier_value: str) -> str:
        """Get display name for privacy tier"""
        tier_names = {
            PrivacyTier.FULL_SUPPORT.value: "Full Support",
            PrivacyTier.ASSISTED_HANDOFF.value: "Assisted Handoff",
            PrivacyTier.YOUR_PRIVATE_NOTES.value: "Your Private Notes",
            PrivacyTier.NO_RECORDS.value: "No Records"
        }
        return tier_names.get(tier_value, "Unknown")
