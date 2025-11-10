"""
Habit Agent - Adaptive Habit Tracking & Recommendations
=======================================================

This agent:
1. Recommends therapeutic habits based on user's issues
2. Tracks completion and progress
3. Adapts difficulty based on success rate
4. Provides encouragement and streak tracking

Powered by: Gemini 2.0 Flash (fast recommendations)
"""

from typing import List
from .base_agent import BaseAgent, AgentState
from models.habit import Habit, HabitFrequency


class HabitAgent(BaseAgent):
    """
    Habit Agent for therapeutic homework tracking.

    Recommends habits, tracks progress, provides encouragement.
    """

    def __init__(self):
        super().__init__(
            agent_name="Habit Coach",
            model_name="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=400
        )

    def get_system_prompt(self) -> str:
        """System prompt for habit recommendations"""
        return """You are a Habit Coach AI that helps users build healthy mental health habits.

Your role:
- Recommend 1-3 simple, actionable habits based on their concerns
- Keep habits small and achievable (start with 5-10 minutes)
- Be encouraging and supportive
- Explain WHY each habit helps

Habit examples:
- Anxiety: Deep breathing, meditation, journaling
- Depression: Morning walk, gratitude journal, sunlight exposure
- Stress: Progressive muscle relaxation, end-of-day decompress
- Sleep issues: No screens before bed, consistent sleep schedule

Keep recommendations warm and encouraging (2-3 sentences)."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Recommend habits based on user's concerns.
        """
        print(f"📊 {self.agent_name} creating habit recommendations...")

        # Extract user's main issues
        user_issues = state.agent_data.get("user_issues", ["general wellness"])

        # Build recommendation context
        context = f"""User is dealing with: {', '.join(user_issues)}

Recommend 2-3 simple daily habits that would help. For each habit:
- Keep it specific and measurable
- Start small (5-15 minutes)
- Explain why it helps

Format as a friendly list."""

        # Generate recommendations
        response_text = self.generate_response(state, context)

        # Add response
        state = self.add_message(state, "assistant", response_text)

        # Create mock habit objects (in production, save to DB)
        recommended_habits = self._create_habit_recommendations(user_issues)
        state.agent_data["recommended_habits"] = [h.dict() for h in recommended_habits]
        state.agent_data["habit_complete"] = True

        print(f"✅ Recommended {len(recommended_habits)} habits")

        return state

    def _create_habit_recommendations(self, issues: List[str]) -> List[Habit]:
        """
        Create habit objects based on user's issues.
        Mock implementation - would be more sophisticated in production.
        """
        habit_map = {
            "anxiety": Habit(
                id="habit_001",
                user_id="user_temp",
                name="5-minute breathing exercise",
                description="Box breathing: Inhale 4s, hold 4s, exhale 4s, hold 4s",
                frequency=HabitFrequency.DAILY,
                duration_minutes=5,
                difficulty_level=1
            ),
            "depression": Habit(
                id="habit_002",
                user_id="user_temp",
                name="10-minute morning walk",
                description="Walk outside for sunlight exposure and movement",
                frequency=HabitFrequency.DAILY,
                duration_minutes=10,
                difficulty_level=1
            ),
            "stress": Habit(
                id="habit_003",
                user_id="user_temp",
                name="Evening wind-down routine",
                description="15 minutes before bed to decompress and reflect",
                frequency=HabitFrequency.DAILY,
                duration_minutes=15,
                difficulty_level=1
            )
        }

        # Select habits based on issues
        habits = []
        for issue in issues:
            if issue in habit_map:
                habits.append(habit_map[issue])

        # Default to breathing exercise if no specific match
        if not habits:
            habits.append(habit_map["anxiety"])

        return habits[:3]  # Max 3 habits
