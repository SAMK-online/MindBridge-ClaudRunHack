"""
Base Agent - Foundation for all NimaCare agents
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import google.generativeai as genai
import os


class AgentMessage(BaseModel):
    """Single message in conversation"""
    role: str  # "user" or "assistant"
    content: str


class AgentState(BaseModel):
    """State shared across all agents"""
    messages: List[AgentMessage] = []
    agent_data: Dict[str, Any] = {}
    user_id: Optional[str] = None
    current_agent: Optional[str] = None


class BaseAgent:
    """
    Base class for all NimaCare AI agents.

    Each agent uses Gemini models and maintains conversation state.
    """

    def __init__(
        self,
        agent_name: str,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        self.agent_name = agent_name
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Configure Gemini with API key only (no service account)
        # Explicitly remove service account credentials to avoid SSL issues
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None
            print(f"⚠️  {agent_name}: No API key - running in demo mode")

    def get_system_prompt(self) -> str:
        """Override this in each agent"""
        return f"You are {self.agent_name}, an empathetic AI assistant."

    def add_message(self, state: AgentState, role: str, content: str) -> AgentState:
        """Add a message to the conversation"""
        state.messages.append(AgentMessage(role=role, content=content))
        return state

    def get_last_user_message(self, state: AgentState) -> Optional[str]:
        """Get the most recent user message"""
        for msg in reversed(state.messages):
            if msg.role == "user":
                return msg.content
        return None

    def generate_response(self, state: AgentState, context: Optional[str] = None) -> str:
        """
        Generate response using Gemini.

        Args:
            state: Current conversation state
            context: Additional context for this specific response

        Returns:
            Generated response text
        """
        if not self.model:
            return f"[{self.agent_name} - Demo mode: API not configured]"

        # Build prompt - pass state for context-aware system prompts
        try:
            system_prompt = self.get_system_prompt(state)
        except TypeError:
            # Fallback for agents that don't accept state parameter yet
            system_prompt = self.get_system_prompt()

        # Add conversation history
        conversation = []
        for msg in state.messages:
            conversation.append(f"{msg.role}: {msg.content}")

        conversation_text = "\n".join(conversation)

        # Build full prompt
        full_prompt = f"""{system_prompt}

{context if context else ''}

Conversation history:
{conversation_text}

Respond as the assistant (keep it concise, 2-3 sentences):"""

        # Debug logging disabled for production
        # Uncomment below to debug prompts
        # print(f"\n📝 {self.agent_name} Prompt: {full_prompt[:100]}...")

        try:
            # Configure safety settings for mental health content
            # Allow mental health discussions while maintaining safety
            from google.generativeai.types import HarmCategory, HarmBlockThreshold

            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }

            # Generate with Gemini
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                ),
                safety_settings=safety_settings
            )

            # Context-aware fallback responses that reference what user said
            def get_fallback(turn_count, user_message=""):
                # Extract key topics from user message
                user_lower = user_message.lower() if user_message else ""

                # Detect topic areas
                is_career = any(word in user_lower for word in ["work", "job", "career", "burnout", "boss"])
                is_relationship = any(word in user_lower for word in ["relationship", "partner", "spouse", "marriage", "family"])
                is_anxiety = any(word in user_lower for word in ["anxious", "anxiety", "panic", "worried", "stress"])
                is_depression = any(word in user_lower for word in ["depressed", "depression", "sad", "hopeless", "empty"])

                # First response - always warm greeting
                if turn_count == 1:
                    return "Hi there. I'm Nima, and I'm here to listen. How are you feeling right now, and what brings you here today?"

                # Second response - acknowledge and explore
                if turn_count == 2:
                    if is_career:
                        return "Work challenges can feel overwhelming, especially when they're affecting your well-being. Can you tell me more about what's been happening? What aspects of your work situation feel most difficult right now?"
                    elif is_relationship:
                        return "Relationship struggles can be really hard to navigate. I hear that this is weighing on you. What's been going on that made you decide to reach out today?"
                    elif is_anxiety:
                        return "Anxiety can be exhausting to deal with. Thank you for trusting me with this. Can you share more about when you tend to feel most anxious, or what situations trigger it for you?"
                    elif is_depression:
                        return "I'm glad you're here. Depression can make everything feel heavier. How long have you been feeling this way, and what does a typical day look like for you right now?"
                    else:
                        return "I appreciate you opening up about what you're going through. That takes courage. Can you tell me more about what's been weighing on you lately?"

                # Third response - go deeper
                if turn_count == 3:
                    if is_career:
                        return "It sounds like work has been taking a real toll on you. When you think about your career situation, what feels most urgent or concerning? Is it the day-to-day stress, or is it more about the bigger picture of where you're headed?"
                    elif is_anxiety or is_depression:
                        return "What you're experiencing sounds really challenging. Have these feelings been building up gradually, or was there a particular moment when things felt like they shifted? And how is this affecting other parts of your life?"
                    else:
                        return "I'm hearing that this is really affecting you. What would it look like if things were better? What are you hoping could change?"

                # Fourth+ response - transition to counselor
                return "Thank you for sharing all of this with me. It's clear you're dealing with something significant, and I think connecting with a professional counselor could really help. Would you like me to match you with someone who specializes in what you're going through?"

            # Check if response was blocked
            if not response.candidates:
                print(f"❌ {self.agent_name}: No candidates returned")
                print(f"   Safety ratings: {response.prompt_feedback}")
                turn_count = len([m for m in state.messages if m.role == "user"])
                last_user_msg = self.get_last_user_message(state) or ""
                return get_fallback(turn_count, last_user_msg)

            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                print(f"❌ {self.agent_name}: Content blocked")
                print(f"   Finish reason: {candidate.finish_reason}")
                print(f"   Safety ratings: {candidate.safety_ratings}")
                turn_count = len([m for m in state.messages if m.role == "user"])
                last_user_msg = self.get_last_user_message(state) or ""
                return get_fallback(turn_count, last_user_msg)

            return response.text.strip()

        except Exception as e:
            print(f"❌ {self.agent_name} generation error: {e}")
            # Use context-aware fallback on exception
            turn_count = len([m for m in state.messages if m.role == "user"])
            last_user_msg = self.get_last_user_message(state) or ""

            # Context-aware fallback responses
            user_lower = last_user_msg.lower() if last_user_msg else ""
            is_career = any(word in user_lower for word in ["work", "job", "career", "burnout", "boss"])
            is_relationship = any(word in user_lower for word in ["relationship", "partner", "spouse", "marriage", "family"])
            is_anxiety = any(word in user_lower for word in ["anxious", "anxiety", "panic", "worried", "stress"])
            is_depression = any(word in user_lower for word in ["depressed", "depression", "sad", "hopeless", "empty"])

            if turn_count == 1:
                return "Hi there. I'm Nima, and I'm here to listen. How are you feeling right now, and what brings you here today?"
            elif turn_count == 2:
                if is_career:
                    return "Work challenges can feel overwhelming, especially when they're affecting your well-being. Can you tell me more about what's been happening? What aspects of your work situation feel most difficult right now?"
                elif is_anxiety or is_depression:
                    return "I'm glad you're here. What you're describing sounds really difficult. Can you tell me more about what you've been experiencing?"
                else:
                    return "I appreciate you opening up about what you're going through. That takes courage. Can you tell me more about what's been weighing on you lately?"
            else:
                return "Thank you for sharing all of this with me. It's clear you're dealing with something significant, and I think connecting with a professional counselor could really help. Would you like me to match you with someone who specializes in what you're going through?"

    async def process(self, state: AgentState) -> AgentState:
        """
        Process the current state and update it.
        Override this in each specific agent.
        """
        raise NotImplementedError("Each agent must implement process()")
