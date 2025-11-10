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
from datetime import datetime
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

# CORS middleware - production-ready configuration
# Get allowed origins from environment or use secure defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080,https://mindbridge-app.run.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
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
    """Serve the landing page"""
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/app", response_class=HTMLResponse)
async def app_ui(request: Request):
    """Serve the voice interface UI"""
    return templates.TemplateResponse("voice_interface.html", {"request": request})

@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    """Serve the text chat UI"""
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


@app.exception_handler(404)
async def not_found(request: Request, exc):
    """Custom 404 page"""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


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


@app.get("/habits/{session_id}")
async def get_habits(session_id: str):
    """
    Get recommended habits for a session.

    Args:
        session_id: Session identifier

    Returns:
        List of recommended habits
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[session_id]
    habits = state.agent_data.get("recommended_habits", [])

    return {
        "session_id": session_id,
        "habits": habits,
        "category": state.agent_data.get("selected_category") or state.agent_data.get("suggested_category")
    }


class HabitCompletionRequest(BaseModel):
    """Habit completion tracking request"""
    session_id: str
    habit_id: str
    completed: bool
    notes: Optional[str] = None


@app.post("/habits/complete")
async def complete_habit(request: HabitCompletionRequest):
    """
    Mark a habit as completed.

    Args:
        request: Habit completion data

    Returns:
        Updated habit data
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[request.session_id]
    
    # Initialize habit completions if not exists
    if "habit_completions" not in state.agent_data:
        state.agent_data["habit_completions"] = {}

    # Track completion
    if request.habit_id not in state.agent_data["habit_completions"]:
        state.agent_data["habit_completions"][request.habit_id] = {
            "total_completions": 0,
            "current_streak": 0,
            "last_completed": None,
            "history": []
        }

    habit_data = state.agent_data["habit_completions"][request.habit_id]
    
    if request.completed:
        habit_data["total_completions"] += 1
        habit_data["current_streak"] += 1
        habit_data["last_completed"] = datetime.now().isoformat()
    else:
        habit_data["current_streak"] = 0

    habit_data["history"].append({
        "date": datetime.now().isoformat(),
        "completed": request.completed,
        "notes": request.notes
    })

    sessions[request.session_id] = state

    return {
        "success": True,
        "habit_id": request.habit_id,
        "data": habit_data
    }


class ScheduleRequest(BaseModel):
    """Schedule appointment request"""
    session_id: str
    therapist_id: str
    preferred_datetime: str
    notes: Optional[str] = None


@app.post("/schedule")
async def schedule_appointment(request: ScheduleRequest):
    """
    Schedule an appointment with a therapist.

    Args:
        request: Scheduling data

    Returns:
        Appointment details
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[request.session_id]
    
    # Create appointment
    appointment_id = f"appt_{datetime.now().timestamp()}"
    
    appointment = {
        "id": appointment_id,
        "session_id": request.session_id,
        "user_id": state.user_id,
        "therapist_id": request.therapist_id,
        "scheduled_time": request.preferred_datetime,
        "status": "pending",
        "notes": request.notes,
        "created_at": datetime.now().isoformat()
    }

    # Store in session
    if "appointments" not in state.agent_data:
        state.agent_data["appointments"] = []
    
    state.agent_data["appointments"].append(appointment)
    sessions[request.session_id] = state

    return {
        "success": True,
        "appointment": appointment,
        "message": f"Appointment scheduled for {request.preferred_datetime}"
    }


@app.get("/appointments/{session_id}")
async def get_appointments(session_id: str):
    """
    Get appointments for a session.

    Args:
        session_id: Session identifier

    Returns:
        List of appointments
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[session_id]
    appointments = state.agent_data.get("appointments", [])

    return {
        "session_id": session_id,
        "appointments": appointments
    }


class PrivacyRequest(BaseModel):
    """Privacy tier selection request"""
    user_id: str
    session_id: Optional[str] = None
    privacy_tier: str


@app.post("/privacy/set")
async def set_privacy(request: PrivacyRequest):
    """
    Set user privacy tier.

    Args:
        request: Privacy settings

    Returns:
        Confirmation
    """
    # Validate privacy tier
    valid_tiers = ["no_records", "your_private_notes", "assisted_handoff", "full_support"]
    if request.privacy_tier not in valid_tiers:
        raise HTTPException(status_code=400, detail="Invalid privacy tier")

    # If session exists, update it
    if request.session_id and request.session_id in sessions:
        state = sessions[request.session_id]
        state.agent_data["privacy_tier"] = request.privacy_tier
        sessions[request.session_id] = state

    return {
        "success": True,
        "privacy_tier": request.privacy_tier,
        "message": f"Privacy set to {request.privacy_tier}"
    }


@app.get("/contributions/{session_id}")
async def get_agent_contributions(session_id: str):
    """
    Get agent contributions for visualization.

    Args:
        session_id: Session identifier

    Returns:
        List of agent contributions
    """
    if session_id not in sessions:
        return {"contributions": []}

    state = sessions[session_id]
    contributions = []

    # Intake Agent contribution
    if state.agent_data.get("intake_complete"):
        contributions.append({
            "agent": "intake",
            "title": "Intake Agent",
            "content": "Gathered initial context and built rapport"
        })

    # Crisis Agent contribution
    if state.agent_data.get("crisis_complete"):
        crisis_level = state.agent_data.get("crisis_level", "none")
        category = state.agent_data.get("suggested_category", "general")
        contributions.append({
            "agent": "crisis",
            "title": "Crisis Agent",
            "content": f"Risk Level: {crisis_level.upper()} • Suggested: {category.title()} counselor"
        })

    # Resource Agent contribution
    if state.agent_data.get("resource_complete"):
        therapist_count = len(state.agent_data.get("matched_therapists", []))
        category = state.agent_data.get("selected_category", "general")
        contributions.append({
            "agent": "resource",
            "title": "Resource Agent",
            "content": f"Matched {therapist_count} {category.title()} specialists"
        })

    # Habit Agent contribution
    if state.agent_data.get("habit_complete"):
        habits_count = len(state.agent_data.get("recommended_habits", []))
        contributions.append({
            "agent": "habit",
            "title": "Habit Agent",
            "content": f"Recommended {habits_count} evidence-based habits"
        })

    return {"contributions": contributions}


# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
