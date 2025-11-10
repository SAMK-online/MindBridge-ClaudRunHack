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
        "suggested_category": state.agent_data.get("suggested_category"),
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
        Updated habit data with streak information
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
            "longest_streak": 0,
            "last_completed": None,
            "history": []
        }

    habit_data = state.agent_data["habit_completions"][request.habit_id]

    if request.completed:
        habit_data["total_completions"] += 1
        habit_data["current_streak"] += 1
        habit_data["last_completed"] = datetime.now().isoformat()

        # Update longest streak
        if habit_data["current_streak"] > habit_data.get("longest_streak", 0):
            habit_data["longest_streak"] = habit_data["current_streak"]
    else:
        habit_data["current_streak"] = 0

    habit_data["history"].append({
        "date": datetime.now().isoformat(),
        "completed": request.completed,
        "notes": request.notes
    })

    sessions[request.session_id] = state

    # Check for milestone achievements
    milestones = [7, 14, 30, 60, 90, 180, 365]
    milestone_reached = None
    for milestone in milestones:
        if habit_data["current_streak"] == milestone:
            milestone_reached = milestone
            break

    return {
        "success": True,
        "habit_id": request.habit_id,
        "data": habit_data,
        "milestone_reached": milestone_reached,
        "streak_message": f"🔥 {habit_data['current_streak']} day streak!" if habit_data["current_streak"] > 0 else None
    }


@app.get("/habits/{session_id}/stats")
async def get_habit_stats(session_id: str, habit_id: Optional[str] = None):
    """
    Get habit statistics including streaks and milestones.

    Args:
        session_id: Session identifier
        habit_id: Optional habit ID to get specific habit stats

    Returns:
        Habit statistics
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[session_id]

    habit_completions = state.agent_data.get("habit_completions", {})

    if habit_id:
        # Return stats for specific habit
        if habit_id not in habit_completions:
            raise HTTPException(status_code=404, detail="Habit not found")

        habit_data = habit_completions[habit_id]

        # Calculate completion rate
        total_days = len(habit_data["history"])
        completed_days = habit_data["total_completions"]
        completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0

        return {
            "habit_id": habit_id,
            "total_completions": habit_data["total_completions"],
            "current_streak": habit_data["current_streak"],
            "longest_streak": habit_data.get("longest_streak", habit_data["current_streak"]),
            "completion_rate": round(completion_rate, 1),
            "last_completed": habit_data.get("last_completed"),
            "total_days": total_days
        }
    else:
        # Return stats for all habits
        all_stats = []

        for hid, data in habit_completions.items():
            total_days = len(data["history"])
            completed_days = data["total_completions"]
            completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0

            all_stats.append({
                "habit_id": hid,
                "total_completions": data["total_completions"],
                "current_streak": data["current_streak"],
                "longest_streak": data.get("longest_streak", data["current_streak"]),
                "completion_rate": round(completion_rate, 1),
                "last_completed": data.get("last_completed")
            })

        return {
            "session_id": session_id,
            "habits": all_stats,
            "total_habits": len(all_stats)
        }


@app.get("/habits/{session_id}/{habit_id}/history")
async def get_habit_history(session_id: str, habit_id: str, limit: int = 30):
    """
    Get habit completion history.

    Args:
        session_id: Session identifier
        habit_id: Habit identifier
        limit: Number of recent entries to return (default: 30)

    Returns:
        Habit completion history
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[session_id]

    habit_completions = state.agent_data.get("habit_completions", {})

    if habit_id not in habit_completions:
        raise HTTPException(status_code=404, detail="Habit not found")

    habit_data = habit_completions[habit_id]
    history = habit_data.get("history", [])

    # Return most recent entries
    recent_history = history[-limit:] if len(history) > limit else history

    return {
        "habit_id": habit_id,
        "history": recent_history,
        "total_entries": len(history)
    }


class BookingRequest(BaseModel):
    """Session booking request"""
    session_id: str
    category: str
    privacy_tier: str
    time_slot: str


@app.post("/book-session")
async def book_session(request: BookingRequest):
    """
    Book a therapy session with matched therapist.
    
    Args:
        request: Booking details
    
    Returns:
        Booking confirmation with therapist details
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[request.session_id]
    
    # Get matched therapists for the category
    from agents.resource_agent import ResourceAgent
    resource_agent = ResourceAgent()
    
    # Get therapists for the selected category
    therapists = resource_agent._get_available_therapists(request.category)
    
    if not therapists:
        raise HTTPException(status_code=404, detail="No therapists available")
    
    # Select first available therapist (or random)
    import random
    selected_therapist = random.choice(therapists)
    
    # Create booking
    booking_id = f"booking_{datetime.now().timestamp()}"
    booking = {
        "id": booking_id,
        "session_id": request.session_id,
        "user_id": state.user_id,
        "therapist_id": selected_therapist.id,
        "therapist_name": selected_therapist.name,
        "category": request.category,
        "privacy_tier": request.privacy_tier,
        "time_slot": request.time_slot,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    # Store booking in session
    if "bookings" not in state.agent_data:
        state.agent_data["bookings"] = []
    
    state.agent_data["bookings"].append(booking)
    state.agent_data["selected_category"] = request.category
    state.agent_data["therapist_match_found"] = True
    state.agent_data["matched_therapist_id"] = selected_therapist.id
    
    sessions[request.session_id] = state
    
    return {
        "success": True,
        "booking": booking,
        "therapist": {
            "id": selected_therapist.id,
            "name": selected_therapist.name,
            "bio": selected_therapist.bio,
            "experience": selected_therapist.years_experience
        },
        "message": f"Session booked with {selected_therapist.name}"
    }


class SupportGroupRequest(BaseModel):
    """Support group matching request"""
    session_id: str
    category: str
    available_times: List[str]  # e.g. ["monday_evening", "wednesday_afternoon"]
    notes: Optional[str] = None
    anonymous: bool = True


@app.post("/support-group")
async def match_support_group(request: SupportGroupRequest):
    """
    Match user with an anonymous peer support group using intelligent matching.

    Args:
        request: Support group matching criteria

    Returns:
        Matched support group details with personalized recommendations
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[request.session_id]
    
    # Use Support Group Agent for intelligent matching
    from agents.support_group_agent import SupportGroupAgent
    
    support_agent = SupportGroupAgent()
    
    # Store user preferences in state
    state.agent_data["support_group_preferences"] = {
        "available_times": request.available_times,
        "notes": request.notes,
        "anonymous": request.anonymous
    }
    
    # Process with support group agent
    state = await support_agent.process(state)
    
    # Get matched groups from agent
    matched_groups = state.agent_data.get("available_support_groups", [])
    
    # Create match record
    match_id = f"group_{datetime.now().timestamp()}"
    match = {
        "id": match_id,
        "session_id": request.session_id,
        "user_id": state.user_id,
        "category": request.category,
        "matched_groups": matched_groups,
        "available_times": request.available_times,
        "anonymous": request.anonymous,
        "notes": request.notes,
        "status": "pending_confirmation",
        "created_at": datetime.now().isoformat()
    }

    # Store in session
    if "support_groups" not in state.agent_data:
        state.agent_data["support_groups"] = []
    
    state.agent_data["support_groups"].append(match)
    sessions[request.session_id] = state

    # Get the agent's recommendation message
    last_message = state.messages[-1] if state.messages else None
    recommendation_text = last_message.content if last_message and last_message.role == "assistant" else ""

    return {
        "success": True,
        "match": match,
        "matched_groups": matched_groups,
        "recommendation": recommendation_text,
        "message": f"Intelligently matched {len(matched_groups)} support groups for {request.category}"
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

    # Get scheduled appointment from scheduling agent
    scheduled_appointment = state.agent_data.get("scheduled_appointment")
    appointments = []

    if scheduled_appointment:
        appointments.append(scheduled_appointment)

    # Also get any old-style bookings
    old_bookings = state.agent_data.get("bookings", [])
    appointments.extend(old_bookings)

    return {
        "session_id": session_id,
        "appointments": appointments,
        "scheduling_complete": state.agent_data.get("scheduling_complete", False)
    }


class AppointmentRequest(BaseModel):
    """Appointment creation request"""
    session_id: str
    therapist_id: str
    scheduled_time: str  # ISO format datetime
    session_type: Optional[str] = "initial_consultation"
    notes: Optional[str] = None


@app.post("/appointments/create")
async def create_appointment(request: AppointmentRequest):
    """
    Create a new appointment with a therapist.

    Args:
        request: Appointment details

    Returns:
        Created appointment
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[request.session_id]

    # Create appointment
    from models.appointment import Appointment, AppointmentStatus
    import uuid

    appointment_id = f"appt_{uuid.uuid4().hex[:8]}"

    appointment = {
        "id": appointment_id,
        "user_id": state.user_id,
        "therapist_id": request.therapist_id,
        "scheduled_time": request.scheduled_time,
        "duration_minutes": 60,
        "status": AppointmentStatus.PENDING.value,
        "session_type": request.session_type,
        "notes": request.notes,
        "created_at": datetime.now().isoformat(),
        "confirmed_at": None,
        "cancelled_at": None,
        "reminder_sent": False
    }

    # Store in state
    if "appointments" not in state.agent_data:
        state.agent_data["appointments"] = []

    state.agent_data["appointments"].append(appointment)
    sessions[request.session_id] = state

    return {
        "success": True,
        "appointment": appointment
    }


@app.get("/appointments/{session_id}/available-slots")
async def get_available_slots(session_id: str, therapist_id: Optional[str] = None):
    """
    Get available time slots for scheduling.

    Args:
        session_id: Session identifier
        therapist_id: Optional therapist ID to filter slots

    Returns:
        List of available time slots
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[session_id]

    # Get available slots from scheduling agent
    available_slots = state.agent_data.get("available_slots", [])

    # Filter by therapist if specified
    if therapist_id:
        available_slots = [slot for slot in available_slots if slot.get("therapist_id") == therapist_id]

    return {
        "session_id": session_id,
        "available_slots": available_slots,
        "count": len(available_slots)
    }


class AppointmentUpdateRequest(BaseModel):
    """Appointment update request"""
    session_id: str
    appointment_id: str
    status: str  # pending, confirmed, cancelled, completed, no_show


@app.put("/appointments/update")
async def update_appointment(request: AppointmentUpdateRequest):
    """
    Update appointment status.

    Args:
        request: Update details

    Returns:
        Updated appointment
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    state = sessions[request.session_id]

    # Find and update appointment
    appointments = state.agent_data.get("appointments", [])
    updated_appointment = None

    for apt in appointments:
        if apt["id"] == request.appointment_id:
            apt["status"] = request.status

            if request.status == "confirmed":
                apt["confirmed_at"] = datetime.now().isoformat()
            elif request.status == "cancelled":
                apt["cancelled_at"] = datetime.now().isoformat()

            updated_appointment = apt
            break

    if not updated_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    sessions[request.session_id] = state

    return {
        "success": True,
        "appointment": updated_appointment
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
