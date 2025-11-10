"""
Support Group Agent - Intelligent Peer Support Matching
=======================================================

This agent intelligently matches users with anonymous peer support groups
based on:
1. Their mental health concerns (category)
2. Available times and timezone
3. Group size and composition
4. Personality matching (quiet vs. active)
5. Specific needs (e.g., new to therapy, long-term support)

Powered by: Gemini 2.0 Flash (fast matching with smart recommendations)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentState
from enum import Enum


class GroupSize(str, Enum):
    """Support group sizes"""
    SMALL = "small"      # 4-6 people
    MEDIUM = "medium"    # 7-10 people
    LARGE = "large"      # 11-15 people


class GroupStyle(str, Enum):
    """Support group interaction styles"""
    QUIET = "quiet"           # More listening, less pressure to share
    BALANCED = "balanced"     # Mix of sharing and listening
    ACTIVE = "active"         # Encouraging everyone to participate


class SupportGroup:
    """Support group data model"""
    def __init__(
        self,
        id: str,
        name: str,
        category: str,
        size: GroupSize,
        current_members: int,
        style: GroupStyle,
        meeting_time: str,
        timezone: str = "EST",
        description: str = "",
        facilitator: str = "",
        tags: List[str] = None
    ):
        self.id = id
        self.name = name
        self.category = category
        self.size = size
        self.current_members = current_members
        self.style = style
        self.meeting_time = meeting_time
        self.timezone = timezone
        self.description = description
        self.facilitator = facilitator
        self.tags = tags or []


class SupportGroupAgent(BaseAgent):
    """
    Support Group Agent for intelligent peer support matching.
    
    Uses smart matching algorithms to:
    - Match users with groups that fit their needs
    - Consider time availability and preferences
    - Balance group sizes and dynamics
    - Provide personalized recommendations
    """

    def __init__(self):
        super().__init__(
            agent_name="Support Group Coordinator",
            model_name="gemini-2.5-flash",
            temperature=0.5,  # Balanced for personalized recommendations
            max_tokens=500
        )

    def get_system_prompt(self, state: AgentState = None) -> str:
        """System prompt for support group matching"""
        
        # Get context from previous agents
        context = ""
        if state:
            category = state.agent_data.get("selected_category", "general")
            crisis_level = state.agent_data.get("crisis_level", "none")
            
            context = f"""
CONTEXT FROM PREVIOUS SESSIONS:
- Primary concern: {category.title()}
- Risk level: {crisis_level.upper()}
- User has already been matched with a therapist

Your role is to find the BEST peer support group for this user as a complement to their therapy.
"""
        
        return f"""You are a Support Group Coordinator AI specializing in peer support matching.

{context}

Your task:
1. Understand the user's preferences for group support
2. Consider their schedule and comfort level
3. Match them with the most suitable peer support group
4. Explain why each recommended group is a good fit

Group Types Available:
- Small (4-6 people): Intimate, everyone shares
- Medium (7-10 people): Balanced group dynamics
- Large (11-15 people): More perspectives, can listen more

Group Styles:
- Quiet: Low pressure, mostly listening
- Balanced: Equal sharing and listening
- Active: Everyone encouraged to participate

Be warm, understanding, and help them find the right fit. Some people need quiet groups,
others thrive in active discussions. Match them to their comfort zone.

Keep recommendations concise (2-3 sentences per group)."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Match user with appropriate support groups.
        """
        print(f"👥 {self.agent_name} matching support groups...")

        # Get user's category and preferences
        selected_category = state.agent_data.get("selected_category", "general")
        user_preferences = state.agent_data.get("support_group_preferences", {})
        
        print(f"📋 Matching for category: {selected_category}")

        # Get available groups for this category
        available_groups = self._get_available_groups(selected_category)
        
        if not available_groups:
            response_text = (
                "I don't have any active support groups for your specific category right now, "
                "but I can connect you with our General Mental Wellness group which welcomes everyone. "
                "Would you like to join that one?"
            )
        else:
            # Build context for AI recommendation
            groups_context = self._format_groups_for_ai(available_groups)
            
            context = f"""Here are the available support groups for {selected_category}:

{groups_context}

Based on the user's conversation, recommend the 2-3 BEST matches and explain why each would be a good fit.
Be concise but personal."""

            # Generate personalized recommendation
            response_text = self.generate_response(state, context)
        
        # Add response to state
        state = self.add_message(state, "assistant", response_text)

        # Store matched groups in state
        state.agent_data["available_support_groups"] = [
            {
                "id": g.id,
                "name": g.name,
                "category": g.category,
                "meeting_time": g.meeting_time,
                "size": g.size.value,
                "style": g.style.value,
                "current_members": g.current_members,
                "description": g.description
            }
            for g in available_groups
        ]
        
        state.agent_data["support_group_matching_complete"] = True

        print(f"✅ Matched {len(available_groups)} support groups")

        return state

    def _get_available_groups(self, category: str) -> List[SupportGroup]:
        """
        Get available support groups for a category.
        Smart matching based on category and availability.
        """
        # Comprehensive support group database
        all_groups = {
            "depression": [
                SupportGroup(
                    id="dep_group_001",
                    name="Hope & Healing Circle",
                    category="depression",
                    size=GroupSize.MEDIUM,
                    current_members=8,
                    style=GroupStyle.BALANCED,
                    meeting_time="Mondays 7pm EST",
                    description="Supportive space for those navigating depression. Focus on small wins and mutual encouragement.",
                    facilitator="Peer-led with licensed therapist",
                    tags=["weekly", "evening", "long-term-support"]
                ),
                SupportGroup(
                    id="dep_group_002",
                    name="Rising Together",
                    category="depression",
                    size=GroupSize.SMALL,
                    current_members=5,
                    style=GroupStyle.QUIET,
                    meeting_time="Fridays 8pm EST",
                    description="Intimate group for quiet reflection and gentle support. No pressure to share every week.",
                    facilitator="Peer-led",
                    tags=["weekly", "evening", "low-pressure"]
                ),
            ],
            "anxiety": [
                SupportGroup(
                    id="anx_group_001",
                    name="Calm Minds Collective",
                    category="anxiety",
                    size=GroupSize.MEDIUM,
                    current_members=9,
                    style=GroupStyle.BALANCED,
                    meeting_time="Tuesdays 7pm EST",
                    description="Practice anxiety management techniques together. Share coping strategies that work.",
                    facilitator="Licensed therapist facilitated",
                    tags=["weekly", "evening", "skills-based"]
                ),
                SupportGroup(
                    id="anx_group_002",
                    name="Worry Warriors",
                    category="anxiety",
                    size=GroupSize.LARGE,
                    current_members=12,
                    style=GroupStyle.ACTIVE,
                    meeting_time="Thursdays 8pm EST",
                    description="Active group tackling anxiety together. Everyone encouraged to share tips and wins.",
                    facilitator="Peer-led",
                    tags=["weekly", "evening", "active-sharing"]
                ),
            ],
            "career": [
                SupportGroup(
                    id="car_group_001",
                    name="Career Transition Support",
                    category="career",
                    size=GroupSize.MEDIUM,
                    current_members=7,
                    style=GroupStyle.ACTIVE,
                    meeting_time="Wednesdays 6pm EST",
                    description="For professionals navigating career changes, burnout, or finding purpose in work.",
                    facilitator="Career coach facilitated",
                    tags=["weekly", "evening", "career-focused"]
                ),
                SupportGroup(
                    id="car_group_002",
                    name="Work-Life Balance Circle",
                    category="career",
                    size=GroupSize.SMALL,
                    current_members=6,
                    style=GroupStyle.BALANCED,
                    meeting_time="Sundays 2pm EST",
                    description="Small group focused on sustainable work habits and preventing burnout.",
                    facilitator="Peer-led",
                    tags=["weekly", "afternoon", "work-life-balance"]
                ),
            ],
            "trauma": [
                SupportGroup(
                    id="tra_group_001",
                    name="Healing Paths",
                    category="trauma",
                    size=GroupSize.SMALL,
                    current_members=5,
                    style=GroupStyle.QUIET,
                    meeting_time="Thursdays 7pm EST",
                    description="Safe, gentle space for trauma survivors. Share at your own pace.",
                    facilitator="Trauma-informed therapist",
                    tags=["weekly", "evening", "trauma-informed", "safe-space"]
                ),
            ],
            "grief": [
                SupportGroup(
                    id="gri_group_001",
                    name="Together in Loss",
                    category="grief",
                    size=GroupSize.MEDIUM,
                    current_members=8,
                    style=GroupStyle.BALANCED,
                    meeting_time="Saturdays 10am EST",
                    description="Compassionate support for those grieving. Share memories, tears, and hope.",
                    facilitator="Grief counselor facilitated",
                    tags=["weekly", "morning", "bereavement"]
                ),
            ],
            "addiction": [
                SupportGroup(
                    id="add_group_001",
                    name="Recovery Circle",
                    category="addiction",
                    size=GroupSize.MEDIUM,
                    current_members=10,
                    style=GroupStyle.ACTIVE,
                    meeting_time="Mondays & Thursdays 8pm EST",
                    description="Active recovery support. Accountability and celebration of milestones.",
                    facilitator="Recovery specialist",
                    tags=["twice-weekly", "evening", "accountability"]
                ),
            ],
            "general": [
                SupportGroup(
                    id="gen_group_001",
                    name="Mental Wellness Circle",
                    category="general",
                    size=GroupSize.LARGE,
                    current_members=14,
                    style=GroupStyle.BALANCED,
                    meeting_time="Wednesdays 7pm EST",
                    description="Open to all. Share whatever's on your mind in a judgment-free space.",
                    facilitator="Peer-led",
                    tags=["weekly", "evening", "open-topic"]
                ),
                SupportGroup(
                    id="gen_group_002",
                    name="Young Professionals Support",
                    category="general",
                    size=GroupSize.MEDIUM,
                    current_members=9,
                    style=GroupStyle.ACTIVE,
                    meeting_time="Sundays 7pm EST",
                    description="For young professionals (20s-30s) navigating life, relationships, and careers.",
                    facilitator="Peer-led",
                    tags=["weekly", "evening", "young-adults"]
                ),
            ]
        }

        # Get groups for the category (or general as fallback)
        category_groups = all_groups.get(category.lower(), all_groups["general"])
        
        # Smart filtering based on availability and balance
        available = []
        for group in category_groups:
            # Only include groups that aren't full
            max_size = {"small": 6, "medium": 10, "large": 15}
            if group.current_members < max_size[group.size.value]:
                available.append(group)
        
        return available

    def _format_groups_for_ai(self, groups: List[SupportGroup]) -> str:
        """Format groups for AI recommendation context"""
        formatted = []
        for g in groups:
            formatted.append(
                f"**{g.name}** ({g.size.value}, {g.style.value})\n"
                f"  - Time: {g.meeting_time}\n"
                f"  - Members: {g.current_members} currently\n"
                f"  - Style: {g.description}\n"
                f"  - Facilitator: {g.facilitator}"
            )
        return "\n\n".join(formatted)

    def match_by_preferences(
        self,
        groups: List[SupportGroup],
        preferences: Dict[str, Any]
    ) -> List[SupportGroup]:
        """
        Smart matching algorithm based on user preferences.
        
        Preferences can include:
        - preferred_time: "morning", "afternoon", "evening"
        - preferred_size: "small", "medium", "large"
        - preferred_style: "quiet", "balanced", "active"
        - wants_professional: True/False (facilitator preference)
        """
        matched = []
        
        for group in groups:
            score = 0
            
            # Time matching
            if "preferred_time" in preferences:
                pref_time = preferences["preferred_time"].lower()
                if pref_time in group.meeting_time.lower():
                    score += 3
            
            # Size matching
            if "preferred_size" in preferences:
                if preferences["preferred_size"] == group.size.value:
                    score += 2
            
            # Style matching
            if "preferred_style" in preferences:
                if preferences["preferred_style"] == group.style.value:
                    score += 3
            
            # Professional facilitator preference
            if preferences.get("wants_professional", False):
                if "therapist" in group.facilitator.lower() or "coach" in group.facilitator.lower():
                    score += 2
            
            matched.append((group, score))
        
        # Sort by score and return top matches
        matched.sort(key=lambda x: x[1], reverse=True)
        return [group for group, score in matched[:3]]

