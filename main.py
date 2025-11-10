"""
NimaCare - AI-Powered Mental Health Support
===========================================

FastAPI backend for multi-agent system.
Deploys to Google Cloud Run.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from agents.coordinator import CoordinatorAgent
from agents.base_agent import AgentState, AgentMessage

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="NimaCare API",
    description="AI-powered mental health support with multi-agent system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Mount static files (if any)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize coordinator
coordinator = CoordinatorAgent()

# In-memory session storage (use Redis/Firestore in production)
sessions = {}


# Request/Response models
class ChatRequest(BaseModel):
    """User message request"""
    user_id: str
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """AI response"""
    session_id: str
    messages: List[dict]
    current_agent: Optional[str] = None
    workflow_complete: bool = False


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the frontend UI"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "service": "NimaCare API",
        "status": "healthy",
        "version": "1.0.0",
        "agents": ["Intake", "Crisis", "Resource", "Habit"]
    }


@app.get("/health")
async def health():
    """Health check for Cloud Run"""
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles conversation with multi-agent system.

    Args:
        request: User message and session info

    Returns:
        AI response with conversation state
    """
    try:
        # Get or create session
        session_id = request.session_id or f"session_{request.user_id}_{len(sessions)}"

        if session_id not in sessions:
            # Create new session
            sessions[session_id] = AgentState(
                messages=[],
                agent_data={},
                user_id=request.user_id,
                current_agent="intake"
            )

        # Get current state
        state = sessions[session_id]

        # Add user message
        state.messages.append(AgentMessage(
            role="user",
            content=request.message
        ))

        # Process with coordinator
        state = await coordinator.process(state)

        # Save state
        sessions[session_id] = state

        # Build response
        return ChatResponse(
            session_id=session_id,
            messages=[msg.dict() for msg in state.messages],
            current_agent=state.current_agent,
            workflow_complete=state.agent_data.get("workflow_complete", False)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session state.

    Args:
        session_id: Session identifier

    Returns:
        Current session state
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[session_id]

    return {
        "session_id": session_id,
        "user_id": state.user_id,
        "current_agent": state.current_agent,
        "message_count": len(state.messages),
        "workflow_complete": state.agent_data.get("workflow_complete", False),
        "crisis_level": state.agent_data.get("crisis_level"),
        "therapist_matched": state.agent_data.get("therapist_match_found", False)
    }


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session.

    Args:
        session_id: Session identifier

    Returns:
        Confirmation message
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted"}

    raise HTTPException(status_code=404, detail="Session not found")


# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
