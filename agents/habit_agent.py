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

    def get_system_prompt(self, state: AgentState = None) -> str:
        """System prompt for habit recommendations with full context"""
        
        # Get context from all previous agents
        full_context = ""
        if state:
            crisis_level = state.agent_data.get("crisis_level", "none")
            category = state.agent_data.get("selected_category", "general")
            therapist_matched = state.agent_data.get("therapist_match_found", False)
            
            full_context = f"""
CONTEXT FROM PREVIOUS AGENTS:
- Intake Agent: Gathered user's concerns and built rapport
- Crisis Agent: Assessed risk level as {crisis_level.upper()}, suggested {category.title()} counselor
- Resource Agent: {"Successfully matched with therapist" if therapist_matched else "Provided therapist options"}

Use this complete picture to provide personalized, contextual habit recommendations.
Mention how these habits complement the therapy they'll receive.
For example: "While you work with your {category} counselor, these habits will support your progress..."
"""
        
        return f"""You are a Habit Coach AI that helps users build healthy mental health habits.

{full_context}

Your role:
- Recommend 1-3 simple, actionable habits based on their concerns
- Keep habits small and achievable (start with 5-10 minutes)
- Be encouraging and supportive
- Explain WHY each habit helps
- Connect habits to the therapy/counseling they'll receive

Habit examples:
- Anxiety: Deep breathing, meditation, journaling
- Depression: Morning walk, gratitude journal, sunlight exposure
- Stress: Progressive muscle relaxation, end-of-day decompress
- Sleep issues: No screens before bed, consistent sleep schedule

Acknowledge the work of previous agents and show how habits complement professional help.
Keep recommendations warm and encouraging (2-3 sentences)."""

    async def process(self, state: AgentState) -> AgentState:
        """
        Deterministically recommend habits based on counselor category.
        No LLM needed - uses evidence-based habit library.
        """
        print(f"📊 {self.agent_name} creating habit recommendations...")

        # Get the selected counselor category (set by Crisis Agent)
        selected_category = state.agent_data.get("selected_category") or \
                          state.agent_data.get("suggested_category", "general")

        print(f"📋 Creating habits for category: {selected_category}")

        # Deterministically select habits based on category
        recommended_habits = self._get_category_habits(selected_category)

        # Build human-friendly response
        response_text = self._format_habit_response(selected_category, recommended_habits)

        # Add response
        state = self.add_message(state, "assistant", response_text)

        # Store habit data
        state.agent_data["recommended_habits"] = [h.dict() for h in recommended_habits]
        state.agent_data["habit_complete"] = True

        print(f"✅ Recommended {len(recommended_habits)} evidence-based habits")

        return state

    def _get_category_habits(self, category: str) -> List[Habit]:
        """
        Deterministic habit library mapped to counselor categories.
        Evidence-based therapeutic habits for each category.
        """
        habit_library = {
            "depression": [
                Habit(
                    id="dep_001",
                    user_id="user_temp",
                    name="10-minute morning sunlight walk",
                    description="Walk outside for sunlight exposure and gentle movement to boost serotonin",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=10,
                    difficulty_level=1
                ),
                Habit(
                    id="dep_002",
                    user_id="user_temp",
                    name="3-item gratitude journal",
                    description="Write down 3 things you're grateful for before bed",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=1
                ),
                Habit(
                    id="dep_003",
                    user_id="user_temp",
                    name="Social connection check-in",
                    description="Send a message to one friend or family member",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=2
                ),
            ],
            "anxiety": [
                Habit(
                    id="anx_001",
                    user_id="user_temp",
                    name="5-minute box breathing",
                    description="Breathe in 4s, hold 4s, out 4s, hold 4s. Calms nervous system.",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=1
                ),
                Habit(
                    id="anx_002",
                    user_id="user_temp",
                    name="Worry dump journaling",
                    description="Write down all worries for 10 minutes, then close the notebook",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=10,
                    difficulty_level=1
                ),
                Habit(
                    id="anx_003",
                    user_id="user_temp",
                    name="Progressive muscle relaxation",
                    description="Tense and release each muscle group from toes to head",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=15,
                    difficulty_level=2
                ),
            ],
            "career": [
                Habit(
                    id="car_001",
                    user_id="user_temp",
                    name="End-of-day reflection",
                    description="Note 3 wins from the day and 1 area to improve tomorrow",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=10,
                    difficulty_level=1
                ),
                Habit(
                    id="car_002",
                    user_id="user_temp",
                    name="Skills development time",
                    description="Spend 20 minutes learning a new professional skill",
                    frequency=HabitFrequency.WEEKLY,
                    duration_minutes=20,
                    difficulty_level=2
                ),
                Habit(
                    id="car_003",
                    user_id="user_temp",
                    name="Work-life boundary ritual",
                    description="15-minute transition activity between work and personal time",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=15,
                    difficulty_level=1
                ),
            ],
            "marriage": [
                Habit(
                    id="mar_001",
                    user_id="user_temp",
                    name="Daily appreciation moment",
                    description="Tell your partner one thing you appreciate about them",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=2,
                    difficulty_level=1
                ),
                Habit(
                    id="mar_002",
                    user_id="user_temp",
                    name="Weekly date night",
                    description="Dedicated time together without phones or distractions",
                    frequency=HabitFrequency.WEEKLY,
                    duration_minutes=60,
                    difficulty_level=2
                ),
                Habit(
                    id="mar_003",
                    user_id="user_temp",
                    name="Active listening practice",
                    description="Practice reflecting back what your partner says without judgment",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=10,
                    difficulty_level=2
                ),
            ],
            "adhd": [
                Habit(
                    id="adhd_001",
                    user_id="user_temp",
                    name="Morning brain dump",
                    description="Write down all tasks and thoughts to clear mental clutter",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=1
                ),
                Habit(
                    id="adhd_002",
                    user_id="user_temp",
                    name="25-minute focused work block",
                    description="Pomodoro technique: 25min work, 5min break, no distractions",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=25,
                    difficulty_level=2
                ),
                Habit(
                    id="adhd_003",
                    user_id="user_temp",
                    name="Visual task board check",
                    description="Update your visual task list (post-its, whiteboard, app)",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=1
                ),
            ],
            "trauma": [
                Habit(
                    id="tra_001",
                    user_id="user_temp",
                    name="Grounding 5-4-3-2-1",
                    description="Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=1
                ),
                Habit(
                    id="tra_002",
                    user_id="user_temp",
                    name="Safe space visualization",
                    description="Visualize a calm, safe place for 10 minutes",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=10,
                    difficulty_level=2
                ),
                Habit(
                    id="tra_003",
                    user_id="user_temp",
                    name="Body scan meditation",
                    description="Notice sensations in your body without judgment",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=15,
                    difficulty_level=2
                ),
            ],
            "addiction": [
                Habit(
                    id="add_001",
                    user_id="user_temp",
                    name="Craving tracking",
                    description="Log each craving with intensity (1-10) and what triggered it",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=1
                ),
                Habit(
                    id="add_002",
                    user_id="user_temp",
                    name="Alternative activity practice",
                    description="When cravings hit, do your planned alternative for 10 minutes",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=10,
                    difficulty_level=2
                ),
                Habit(
                    id="add_003",
                    user_id="user_temp",
                    name="Support group check-in",
                    description="Attend meeting or message accountability partner",
                    frequency=HabitFrequency.WEEKLY,
                    duration_minutes=60,
                    difficulty_level=2
                ),
            ],
            "grief": [
                Habit(
                    id="gri_001",
                    user_id="user_temp",
                    name="Memory journaling",
                    description="Write about a positive memory of your loved one",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=10,
                    difficulty_level=1
                ),
                Habit(
                    id="gri_002",
                    user_id="user_temp",
                    name="Self-compassion moment",
                    description="Acknowledge your grief without judgment; it's okay to not be okay",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=1
                ),
                Habit(
                    id="gri_003",
                    user_id="user_temp",
                    name="Meaningful connection",
                    description="Reach out to someone who understands your loss",
                    frequency=HabitFrequency.WEEKLY,
                    duration_minutes=30,
                    difficulty_level=2
                ),
            ],
            "general": [
                Habit(
                    id="gen_001",
                    user_id="user_temp",
                    name="5-minute mindfulness",
                    description="Focus on your breath and bring attention to the present moment",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=5,
                    difficulty_level=1
                ),
                Habit(
                    id="gen_002",
                    user_id="user_temp",
                    name="Physical movement",
                    description="Any form of exercise: walk, yoga, stretch, dance",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=15,
                    difficulty_level=1
                ),
                Habit(
                    id="gen_003",
                    user_id="user_temp",
                    name="Sleep hygiene routine",
                    description="Consistent bedtime, no screens 30min before sleep",
                    frequency=HabitFrequency.DAILY,
                    duration_minutes=10,
                    difficulty_level=1
                ),
            ],
        }

        # Return habits for the category, or general habits as fallback
        return habit_library.get(category, habit_library["general"])

    def _format_habit_response(self, category: str, habits: List[Habit]) -> str:
        """
        Create a warm, human-friendly response about the recommended habits.
        """
        response = f"While you wait to connect with your {category} counselor, here are some evidence-based habits that can help:\n\n"

        for i, habit in enumerate(habits, 1):
            response += f"**{i}. {habit.name}** ({habit.duration_minutes} min, {habit.frequency.value})\n"
            response += f"   {habit.description}\n\n"

        response += "These are small steps you can start today. Your counselor can help you build on these once you connect!"

        return response
