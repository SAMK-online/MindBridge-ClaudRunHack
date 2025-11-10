"""
Crisis Agent - ReAct-based Risk Assessment
==========================================

This agent uses Reason + Act (ReAct) pattern to:
1. Analyze user statements for risk indicators
2. Assess crisis level (NONE → IMMEDIATE)
3. Provide appropriate resources and escalation

Powered by: Gemini 2.0 Flash (fast, accurate crisis detection)
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


class CounselorCategory(str, Enum):
    """Types of counselors available"""
    DEPRESSION = "depression"
    ANXIETY = "anxiety"
    CAREER = "career"
    MARRIAGE = "marriage"
    ADHD = "adhd"
    TRAUMA = "trauma"
    ADDICTION = "addiction"
    GRIEF = "grief"
    GENERAL = "general"


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
            model_name="gemini-2.5-flash",
            temperature=0.3,  # Low temp for consistent risk assessment
            max_tokens=400
        )

    def get_system_prompt(self, state: AgentState = None) -> str:
        """System prompt for crisis assessment with context from previous agents"""
        
        # Get context from Intake Agent
        intake_context = ""
        if state and state.agent_data.get("intake_complete"):
            user_concerns = []
            # Extract key concerns from intake
            for msg in state.messages:
                if msg.role == "user":
                    user_concerns.append(msg.content)
            
            if user_concerns:
                intake_context = f"""
CONTEXT FROM INTAKE AGENT:
Our Intake Agent gathered that the user is experiencing: {', '.join(user_concerns[-3:])}
Use this context to inform your assessment.
"""
        
        return f"""You are a Crisis Assessment AI trained to evaluate mental health needs and suggest appropriate counselor types.

{intake_context}

Your task: Analyze the user's messages and:
1. Assess their crisis level
2. Suggest the most appropriate counselor category

Crisis Levels:
- IMMEDIATE: Mentions suicide, self-harm, harming others - needs emergency services NOW
- HIGH: Severe distress, unable to cope, needs urgent professional help
- MODERATE: Significant anxiety/depression, should see therapist soon
- LOW: Mild stress, would benefit from support
- NONE: General conversation, no crisis indicators

Counselor Categories:
- DEPRESSION: Persistent sadness, hopelessness, loss of interest
- ANXIETY: Excessive worry, panic attacks, social anxiety
- CAREER: Work stress, job dissatisfaction, career transitions
- MARRIAGE: Relationship issues, couples counseling
- ADHD: Focus problems, hyperactivity, executive dysfunction
- TRAUMA: Past abuse, PTSD, traumatic events
- ADDICTION: Substance abuse, behavioral addictions
- GRIEF: Loss of loved one, bereavement
- GENERAL: Life coaching, general wellness support

Provide:
1. Crisis level assessment
2. Suggested counselor category (and why)
3. Brief supportive message

When appropriate, acknowledge the information gathered by our Intake Agent.
Be direct, clear, and compassionate."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Assess crisis level and provide appropriate response.
        """
        print(f"🚨 {self.agent_name} assessing risk...")

        # Check if already asked and waiting for confirmation
        if state.agent_data.get("crisis_category_suggested"):
            last_message = self.get_last_user_message(state)
            if last_message:
                confirm_words = ["yes", "sounds good", "that's right", "okay", "sure", "proceed", "continue", "absolutely"]
                if any(word in last_message.lower() for word in confirm_words):
                    state.agent_data["crisis_complete"] = True
                    print("✅ Crisis assessment complete - moving to resource matching")
                    response_text = "Great! Let me connect you with the right resources."
                    state = self.add_message(state, "assistant", response_text)
                else:
                    # User wants different category - acknowledge and move forward
                    state.agent_data["crisis_complete"] = True
                    print("✅ User preference noted - moving to resource matching")
                    response_text = "Understood. Let me find the best match for you."
                    state = self.add_message(state, "assistant", response_text)
            return state

        # First time - do assessment
        # Build assessment context
        conversation = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in state.messages[-10:]  # Last 10 messages
        ])

        context = f"""Assess the crisis level and suggest appropriate counselor category based on this conversation:

{conversation}

Provide your assessment in this format:
LEVEL: [none/low/moderate/high/immediate]
CATEGORY: [depression/anxiety/career/marriage/adhd/trauma/addiction/grief/general]
REASONING: [1 sentence why this category fits]
RESPONSE: [2-3 sentences providing support and explaining the suggestion]"""

        # Generate assessment
        assessment_text = self.generate_response(state, context)

        # Parse assessment
        crisis_level, category, response_text = self._parse_assessment(assessment_text)

        # Store assessment in state
        state.agent_data["crisis_level"] = crisis_level
        state.agent_data["suggested_category"] = category
        state.agent_data["crisis_assessment"] = assessment_text
        state.agent_data["crisis_category_suggested"] = True

        # Add confirmation question
        if category and category != "general":
            response_text = (
                f"{response_text}\n\n"
                f"Based on what you've shared, I think a **{category.title()} Specialist** would be most helpful for you. "
                f"Does that sound right to you?"
            )

        # Add response
        state = self.add_message(state, "assistant", response_text)

        # Set flags for routing
        if crisis_level == CrisisLevel.IMMEDIATE:
            state.agent_data["needs_emergency"] = True
            state.agent_data["crisis_complete"] = True
            print("🚨 IMMEDIATE crisis detected - emergency resources needed")
        elif crisis_level in [CrisisLevel.HIGH, CrisisLevel.MODERATE]:
            state.agent_data["needs_therapist"] = True
            print(f"⚠️  {crisis_level.upper()} risk - therapist matching needed")
        else:
            state.agent_data["needs_therapist"] = False
            print("✅ No immediate crisis detected")

        return state

    def _parse_assessment(self, assessment_text: str) -> tuple[CrisisLevel, str, str]:
        """
        Parse the AI's assessment into crisis level, counselor category, and response.
        """
        lines = assessment_text.split("\n")

        crisis_level = CrisisLevel.NONE
        category = "general"
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

            elif "CATEGORY:" in line_upper:
                # Extract category
                category_text = line.split(":", 1)[1].strip().lower()
                # Match to valid categories
                for cat in CounselorCategory:
                    if cat.value in category_text:
                        category = cat.value
                        break

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

        return crisis_level, category, response_text
