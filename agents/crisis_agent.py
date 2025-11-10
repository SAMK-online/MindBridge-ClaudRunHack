"""
Crisis Agent - ReAct-based Risk Assessment
==========================================

This agent uses Reason + Act (ReAct) pattern to:
1. Analyze user statements for risk indicators
2. Assess crisis level (NONE → IMMEDIATE)
3. Provide appropriate resources and escalation

Powered by: Gemini 1.5 Flash (fast, accurate crisis detection)
"""

from typing import Dict, Any
from enum import Enum
from .base_agent import BaseAgent, AgentState


class CrisisLevel(str, Enum):
    """5-level crisis risk assessment"""
    NONE = "none"              # No crisis indicators
    LOW = "low"                # Minor stress/anxiety
    MODERATE = "moderate"      # Significant distress
    HIGH = "high"              # Serious concern
    IMMEDIATE = "immediate"    # Life-threatening emergency


class CrisisAgent(BaseAgent):
    """
    Crisis Agent for risk assessment and intervention.

    Uses ReAct (Reason + Act) to:
    - Detect risk indicators
    - Assess severity
    - Provide appropriate resources
    """

    def __init__(self):
        super().__init__(
            agent_name="Crisis Specialist",
            model_name="gemini-1.5-flash",
            temperature=0.3,  # Low temp for consistent risk assessment
            max_tokens=400
        )

    def get_system_prompt(self) -> str:
        """System prompt for crisis assessment"""
        return """You are a Crisis Assessment AI trained to evaluate mental health risk.

Your task: Analyze the user's messages and assess their crisis level.

Crisis Levels:
- IMMEDIATE: Mentions suicide, self-harm, harming others - needs emergency services NOW
- HIGH: Severe distress, unable to cope, needs urgent professional help
- MODERATE: Significant anxiety/depression, should see therapist soon
- LOW: Mild stress, would benefit from support
- NONE: General conversation, no crisis indicators

Provide:
1. Crisis level assessment
2. Specific risk indicators you identified
3. Recommended next steps (resources, emergency numbers, therapist matching)

Be direct, clear, and compassionate."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Assess crisis level and provide appropriate response.
        """
        print(f"🚨 {self.agent_name} assessing risk...")

        # Build assessment context
        conversation = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in state.messages[-10:]  # Last 10 messages
        ])

        context = f"""Assess the crisis level based on this conversation:

{conversation}

Provide your assessment in this format:
LEVEL: [none/low/moderate/high/immediate]
INDICATORS: [list key phrases or behaviors indicating risk]
RESPONSE: [2-3 sentences providing support and next steps]"""

        # Generate assessment
        assessment_text = self.generate_response(state, context)

        # Parse assessment
        crisis_level, response_text = self._parse_assessment(assessment_text)

        # Store assessment in state
        state.agent_data["crisis_level"] = crisis_level
        state.agent_data["crisis_assessment"] = assessment_text

        # Add response
        state = self.add_message(state, "assistant", response_text)

        # Set flags for routing
        if crisis_level == CrisisLevel.IMMEDIATE:
            state.agent_data["needs_emergency"] = True
            print("🚨 IMMEDIATE crisis detected - emergency resources needed")
        elif crisis_level in [CrisisLevel.HIGH, CrisisLevel.MODERATE]:
            state.agent_data["needs_therapist"] = True
            print(f"⚠️  {crisis_level.upper()} risk - therapist matching needed")
        else:
            state.agent_data["needs_therapist"] = False
            print("✅ No immediate crisis detected")

        state.agent_data["crisis_complete"] = True

        return state

    def _parse_assessment(self, assessment_text: str) -> tuple[CrisisLevel, str]:
        """
        Parse the AI's assessment into crisis level and response.
        """
        lines = assessment_text.split("\n")

        crisis_level = CrisisLevel.NONE
        response_text = ""

        for line in lines:
            line_upper = line.upper()
            if "LEVEL:" in line_upper:
                # Extract level
                level_text = line.split(":", 1)[1].strip().lower()
                if "immediate" in level_text:
                    crisis_level = CrisisLevel.IMMEDIATE
                elif "high" in level_text:
                    crisis_level = CrisisLevel.HIGH
                elif "moderate" in level_text:
                    crisis_level = CrisisLevel.MODERATE
                elif "low" in level_text:
                    crisis_level = CrisisLevel.LOW

            elif "RESPONSE:" in line_upper:
                # Extract response
                response_text = line.split(":", 1)[1].strip()

        # If no clear response, use the whole text
        if not response_text:
            response_text = assessment_text

        # Add emergency resources for immediate crisis
        if crisis_level == CrisisLevel.IMMEDIATE:
            response_text = (
                f"{response_text}\n\n"
                "🚨 EMERGENCY RESOURCES:\n"
                "• Call 988 (Suicide & Crisis Lifeline)\n"
                "• Text 'HELLO' to 741741 (Crisis Text Line)\n"
                "• Call 911 if in immediate danger"
            )

        return crisis_level, response_text
