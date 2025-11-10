"""
Scheduling Agent - Support Group Signup
========================================

This agent helps users join anonymous peer support groups.

Presents support group options based on their counselor category.
Connects users with community support while they wait for therapy.

Powered by: Deterministic (no LLM needed)
"""

from typing import Optional, List
from datetime import datetime
import uuid
import os
from .base_agent import BaseAgent, AgentState


class SchedulingAgent(BaseAgent):
    """
    Scheduling Agent for support group signup.

    Presents support group options and facilitates signup.
    Deterministic - no LLM calls needed.
    """

    def __init__(self):
        super().__init__(
            agent_name="Support Group Coordinator",
            model_name="gemini-2.5-flash",  # Model set but not used
            temperature=0.7,
            max_tokens=300
        )

    def get_system_prompt(self) -> str:
        """Not used - deterministic agent"""
        return ""

    async def process(self, state: AgentState) -> AgentState:
        """
        Present support group options and facilitate signup.
        Deterministic flow - no LLM needed.
        """
        print(f"👥 {self.agent_name} presenting support group options...")

        # Demo mode: Auto-complete
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        if demo_mode and not state.agent_data.get("scheduling_complete"):
            print("🎬 DEMO MODE: Auto-joining support group")
            selected_category = state.agent_data.get("selected_category") or \
                              state.agent_data.get("suggested_category", "general")

            response_text = f"Perfect! I've added you to the {selected_category.title()} support group waitlist. You'll receive an email with details about the next meeting and how to join anonymously."
            state.agent_data["scheduling_complete"] = True
            state.agent_data["support_group_joined"] = True
            state = self.add_message(state, "assistant", response_text)
            return state

        # Check if already asked
        if state.agent_data.get("scheduling_presented"):
            # User is responding - assume they want to join
            last_message = self.get_last_user_message(state)
            if last_message:
                # Check if user wants to join
                affirmative_words = ["yes", "sure", "okay", "ok", "join", "sign up", "interested", "sounds good"]
                wants_to_join = any(word in last_message.lower() for word in affirmative_words)

                if wants_to_join:
                    print(f"✅ User wants to join support group")

                    # Confirm signup
                    response_text = "Perfect! I've added you to the support group waitlist. You'll receive an email with details about the next meeting and how to join anonymously."
                    state.agent_data["scheduling_complete"] = True
                    state.agent_data["support_group_joined"] = True
                else:
                    # User declined
                    response_text = "No problem! You can always join a support group later if you change your mind. Let's continue with setting up your habit tracker."
                    state.agent_data["scheduling_complete"] = True
                    state.agent_data["support_group_joined"] = False

                state = self.add_message(state, "assistant", response_text)
                return state

        # First time - present support group option
        selected_category = state.agent_data.get("selected_category") or \
                          state.agent_data.get("suggested_category", "general")

        # Present support group signup
        response_text = self._format_support_group_offer(selected_category)
        state = self.add_message(state, "assistant", response_text)
        state.agent_data["scheduling_presented"] = True

        print("✅ Support group option presented")
        return state

    def _format_support_group_offer(self, category: str) -> str:
        """Format support group signup offer"""
        category_display = category.title()

        response = (
            f"While you're connecting with your {category_display} specialist, "
            f"would you like to join an anonymous peer support group?\n\n"

            f"**Why Join a Support Group?**\n"
            f"• Connect with others facing similar {category} challenges\n"
            f"• Share experiences in a safe, judgment-free space\n"
            f"• Get support between your therapy sessions\n"
            f"• Completely anonymous - use any name you like\n\n"

            f"Support groups meet weekly via video chat. "
            f"Would you like me to add you to the waitlist?"
        )

        return response
