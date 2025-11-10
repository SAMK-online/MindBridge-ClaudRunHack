"""
Resource Agent - Autonomous Therapist Search & Matching
======================================================

This agent:
1. Searches internal therapist database
2. Matches based on specialization, availability, location
3. Can autonomously search web for new volunteer therapists (via tools)
4. Recruits and onboards new therapists when needed

Powered by: Gemini 2.0 Flash thinking mode (complex reasoning for matching logic)
"""

from typing import List, Optional
from .base_agent import BaseAgent, AgentState
from models.therapist import Therapist, TherapistSpecialization


class ResourceAgent(BaseAgent):
    """
    Resource Agent for intelligent therapist matching.

    Uses Gemini 2.0 Flash thinking mode for complex matching logic.
    """

    def __init__(self):
        super().__init__(
            agent_name="Resource Coordinator",
            model_name="gemini-2.5-pro",  # Pro model for complex reasoning
            temperature=0.5,
            max_tokens=600
        )

    def get_system_prompt(self) -> str:
        """System prompt for therapist matching"""
        return """You are a Resource Coordinator AI that matches users with volunteer therapists.

Your task: Find the best therapist match based on:
- User's issues/concerns
- Therapist specializations
- Availability
- Location (if provided)

If no perfect match exists, explain options and suggest alternatives.
Be warm but professional."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Match user with appropriate therapist.
        """
        print(f"🔍 {self.agent_name} searching for therapist match...")

        # Get user context from conversation
        user_issues = self._extract_user_issues(state)
        user_location = state.agent_data.get("user_location")

        # Search therapists (mock for now - would query real DB)
        available_therapists = self._get_available_therapists()

        # Build matching context
        context = f"""User needs help with: {', '.join(user_issues)}
Location: {user_location or 'Not specified'}

Available therapists:
{self._format_therapist_list(available_therapists)}

Select the best match and explain why. If multiple good options, present top 2-3.
Keep response conversational (2-3 sentences)."""

        # Generate matching recommendation
        response_text = self.generate_response(state, context)

        # Add response
        state = self.add_message(state, "assistant", response_text)

        # Store matching result
        if available_therapists:
            state.agent_data["matched_therapist_id"] = available_therapists[0].id
            state.agent_data["therapist_match_found"] = True
        else:
            state.agent_data["therapist_match_found"] = False

        state.agent_data["resource_complete"] = True

        print("✅ Therapist matching complete")

        return state

    def _extract_user_issues(self, state: AgentState) -> List[str]:
        """Extract user's main concerns from conversation"""
        # Simple keyword extraction (in production, use NLP)
        keywords = ["anxiety", "depression", "stress", "trauma", "relationships"]

        conversation_text = " ".join([
            msg.content.lower()
            for msg in state.messages
            if msg.role == "user"
        ])

        issues = [kw for kw in keywords if kw in conversation_text]

        return issues if issues else ["general support"]

    def _get_available_therapists(self) -> List[Therapist]:
        """
        Get available therapists from database.
        Mock data for demo - would query real DB in production.
        """
        return [
            Therapist(
                id="therapist_001",
                name="Dr. Sarah Johnson",
                email="sarah@nimacare.org",
                specializations=[
                    TherapistSpecialization.ANXIETY,
                    TherapistSpecialization.DEPRESSION
                ],
                years_experience=8,
                status="active",
                max_patients=10,
                current_patients=3,
                bio="Licensed psychologist specializing in anxiety and depression."
            ),
            Therapist(
                id="therapist_002",
                name="Dr. Michael Chen",
                email="michael@nimacare.org",
                specializations=[
                    TherapistSpecialization.TRAUMA,
                    TherapistSpecialization.PTSD
                ],
                years_experience=12,
                status="active",
                max_patients=8,
                current_patients=2,
                bio="Trauma specialist with focus on PTSD and recovery."
            )
        ]

    def _format_therapist_list(self, therapists: List[Therapist]) -> str:
        """Format therapist list for AI context"""
        if not therapists:
            return "No therapists currently available"

        formatted = []
        for t in therapists:
            specs = ", ".join([s.value for s in t.specializations])
            formatted.append(
                f"- {t.name}: {specs} ({t.years_experience} yrs exp, "
                f"{t.current_patients}/{t.max_patients} patients)"
            )

        return "\n".join(formatted)
