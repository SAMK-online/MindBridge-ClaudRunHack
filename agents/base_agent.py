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
        model_name: str = "gemini-2.0-flash-exp",
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

        # Build prompt
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

        try:
            # Generate with Gemini
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )

            return response.text.strip()

        except Exception as e:
            print(f"❌ {self.agent_name} generation error: {e}")
            return f"I'm here to help. Could you tell me more about what brings you here today?"

    async def process(self, state: AgentState) -> AgentState:
        """
        Process the current state and update it.
        Override this in each specific agent.
        """
        raise NotImplementedError("Each agent must implement process()")
