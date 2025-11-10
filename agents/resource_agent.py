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

    def get_system_prompt(self, state: AgentState = None) -> str:
        """System prompt for therapist matching with context from previous agents"""
        
        # Get context from previous agents
        crisis_context = ""
        if state:
            crisis_level = state.agent_data.get("crisis_level", "none")
            suggested_category = state.agent_data.get("suggested_category", "general")
            
            crisis_context = f"""
CONTEXT FROM PREVIOUS AGENTS:
- Our Crisis Assessment team determined: Risk Level = {crisis_level.upper()}
- Suggested counselor specialization: {suggested_category.title()}

Use this context to provide personalized therapist recommendations.
Acknowledge the Crisis Agent's assessment when introducing therapist matches.
"""
        
        return f"""You are a Resource Coordinator AI that matches users with volunteer therapists.

{crisis_context}

Your task: Find the best therapist match based on:
- User's issues/concerns  
- Therapist specializations
- Availability
- Location (if provided)

When presenting matches, reference the Crisis Agent's findings to show continuity.
For example: "Based on our Crisis Assessment showing {state.agent_data.get('crisis_level', 'moderate')} anxiety..."

If no perfect match exists, explain options and suggest alternatives.
Be warm but professional."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Match user with appropriate therapist based on selected category.
        """
        print(f"🔍 {self.agent_name} searching for therapist match...")

        # Get selected category from crisis agent (or let user override)
        selected_category = state.agent_data.get("selected_category") or \
                          state.agent_data.get("suggested_category", "general")

        # Check if user wants to override category
        last_message = self.get_last_user_message(state)
        if last_message:
            # Check for category override in user's message
            override_category = self._detect_category_override(last_message)
            if override_category:
                selected_category = override_category
                state.agent_data["selected_category"] = override_category
                print(f"✏️  User selected category: {override_category}")

        # Search therapists filtered by category
        available_therapists = self._get_available_therapists(category_filter=selected_category)

        print(f"📋 Found {len(available_therapists)} therapists for category: {selected_category}")

        if not available_therapists:
            # No therapists for this category
            response_text = (
                f"I apologize, but we don't currently have available counselors specializing in {selected_category}. "
                f"However, our general counselors are trained to help with a wide range of issues. "
                f"Would you like me to connect you with a general counselor instead?"
            )
        else:
            # Build matching context
            context = f"""User needs a {selected_category} counselor.

Available {selected_category} counselors:
{self._format_therapist_list(available_therapists)}

Present the top 2-3 counselors as options. Be warm and explain briefly what makes each a good fit.
Keep response conversational (3-4 sentences)."""

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
        
        # Add proactive handoff message to Habit Agent
        handoff_message = (
            "\n\n---\n\n"
            "💡 **Next Step**: Our Habit Coach will now recommend some evidence-based practices "
            "to support you while you connect with your counselor. These simple daily habits "
            "can make a real difference in your mental wellness journey."
        )
        state = self.add_message(state, "assistant", handoff_message)

        return state

    def _detect_category_override(self, message: str) -> Optional[str]:
        """Detect if user wants a different counselor category"""
        message_lower = message.lower()

        categories = {
            "depression": ["depression", "depressed"],
            "anxiety": ["anxiety", "anxious", "panic"],
            "career": ["career", "job", "work"],
            "marriage": ["marriage", "couple", "relationship"],
            "adhd": ["adhd", "attention", "focus"],
            "trauma": ["trauma", "ptsd", "abuse"],
            "addiction": ["addiction", "substance", "alcohol", "drugs"],
            "grief": ["grief", "loss", "bereavement"],
        }

        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category

        return None

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

    def _get_available_therapists(self, category_filter: Optional[str] = None) -> List[Therapist]:
        """
        Get available therapists from database, filtered by category.
        Mock data for demo - would query real DB in production.
        """
        # Complete therapist database
        all_therapists = [
            # Depression specialists
            Therapist(
                id="therapist_001",
                name="Dr. Sarah Johnson",
                email="sarah@nimacare.org",
                specializations=[TherapistSpecialization.DEPRESSION, TherapistSpecialization.ANXIETY],
                years_experience=8,
                status="active",
                max_patients=10,
                current_patients=3,
                bio="Licensed psychologist specializing in depression and anxiety disorders."
            ),
            # Anxiety specialists
            Therapist(
                id="therapist_002",
                name="Dr. Emily Rodriguez",
                email="emily@nimacare.org",
                specializations=[TherapistSpecialization.ANXIETY, TherapistSpecialization.OCD],
                years_experience=10,
                status="active",
                max_patients=12,
                current_patients=5,
                bio="Cognitive-behavioral therapist specializing in anxiety and OCD treatment."
            ),
            # Career counselors
            Therapist(
                id="therapist_003",
                name="James Patterson",
                email="james@nimacare.org",
                specializations=[TherapistSpecialization.CAREER, TherapistSpecialization.GENERAL],
                years_experience=15,
                status="active",
                max_patients=15,
                current_patients=7,
                bio="Career counselor with expertise in work-life balance and professional development."
            ),
            # Marriage counselors
            Therapist(
                id="therapist_004",
                name="Dr. Lisa Martinez",
                email="lisa@nimacare.org",
                specializations=[TherapistSpecialization.MARRIAGE, TherapistSpecialization.RELATIONSHIPS],
                years_experience=12,
                status="active",
                max_patients=10,
                current_patients=4,
                bio="Licensed marriage and family therapist specializing in couples counseling."
            ),
            # ADHD specialists
            Therapist(
                id="therapist_005",
                name="Dr. David Kim",
                email="david@nimacare.org",
                specializations=[TherapistSpecialization.ADHD],
                years_experience=9,
                status="active",
                max_patients=8,
                current_patients=3,
                bio="ADHD specialist helping adults manage attention and executive function challenges."
            ),
            # Trauma specialists
            Therapist(
                id="therapist_006",
                name="Dr. Michael Chen",
                email="michael@nimacare.org",
                specializations=[TherapistSpecialization.TRAUMA, TherapistSpecialization.PTSD],
                years_experience=12,
                status="active",
                max_patients=8,
                current_patients=2,
                bio="Trauma specialist with focus on PTSD and recovery using EMDR therapy."
            ),
            # Addiction counselors
            Therapist(
                id="therapist_007",
                name="Robert Thompson",
                email="robert@nimacare.org",
                specializations=[TherapistSpecialization.ADDICTION],
                years_experience=14,
                status="active",
                max_patients=10,
                current_patients=6,
                bio="Certified addiction counselor specializing in substance abuse recovery."
            ),
            # Grief counselors
            Therapist(
                id="therapist_008",
                name="Dr. Rachel Green",
                email="rachel@nimacare.org",
                specializations=[TherapistSpecialization.GRIEF],
                years_experience=11,
                status="active",
                max_patients=10,
                current_patients=4,
                bio="Grief counselor helping individuals navigate loss and bereavement."
            ),
            # General counselors
            Therapist(
                id="therapist_009",
                name="Dr. Amanda Foster",
                email="amanda@nimacare.org",
                specializations=[TherapistSpecialization.GENERAL, TherapistSpecialization.ANXIETY],
                years_experience=7,
                status="active",
                max_patients=15,
                current_patients=8,
                bio="General counselor providing holistic mental health support for various concerns."
            ),
        ]

        # Filter by category if specified
        if category_filter and category_filter != "general":
            filtered = []
            for therapist in all_therapists:
                # Check if therapist has the requested specialization
                spec_values = [s.value for s in therapist.specializations]
                if category_filter in spec_values:
                    filtered.append(therapist)
            return filtered

        return all_therapists

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
