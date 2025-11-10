"""
Appointment Model - Therapy session appointments
"""

from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AppointmentStatus(str, Enum):
    """Appointment status"""
    PENDING = "pending"          # Waiting for confirmation
    CONFIRMED = "confirmed"      # Confirmed by both parties
    CANCELLED = "cancelled"      # Cancelled
    COMPLETED = "completed"      # Session completed
    NO_SHOW = "no_show"         # User didn't show up


class Appointment(BaseModel):
    """Therapy session appointment"""

    # Identification
    id: str = Field(..., description="Unique appointment ID")
    user_id: str = Field(..., description="User ID")
    therapist_id: str = Field(..., description="Therapist ID")

    # Scheduling
    scheduled_time: datetime = Field(..., description="Appointment date/time")
    duration_minutes: int = Field(default=60, description="Session duration")
    timezone: str = Field(default="America/New_York", description="Timezone")

    # Status
    status: AppointmentStatus = Field(
        default=AppointmentStatus.PENDING,
        description="Appointment status"
    )

    # Session details
    session_type: str = Field(
        default="initial_consultation",
        description="Type of session"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Session notes (therapist only)"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When appointment was created"
    )
    confirmed_at: Optional[datetime] = Field(
        None,
        description="When appointment was confirmed"
    )
    cancelled_at: Optional[datetime] = Field(
        None,
        description="When appointment was cancelled"
    )

    # Reminders
    reminder_sent: bool = Field(
        default=False,
        description="Whether reminder was sent"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "appt_001",
                "user_id": "user_001",
                "therapist_id": "therapist_003",
                "scheduled_time": "2025-11-12T18:30:00",
                "duration_minutes": 60,
                "status": "confirmed",
                "session_type": "initial_consultation"
            }
        }


class AvailableSlot(BaseModel):
    """Available time slot for booking"""

    therapist_id: str = Field(..., description="Therapist offering this slot")
    therapist_name: str = Field(..., description="Therapist name for display")
    start_time: datetime = Field(..., description="Slot start time")
    duration_minutes: int = Field(default=60, description="Slot duration")
    is_available: bool = Field(default=True, description="Still available?")

    @property
    def display_time(self) -> str:
        """Human-readable time display"""
        return self.start_time.strftime("%A • %I:%M %p")

    class Config:
        json_schema_extra = {
            "example": {
                "therapist_id": "therapist_003",
                "therapist_name": "James Patterson",
                "start_time": "2025-11-12T18:30:00",
                "duration_minutes": 60,
                "display_time": "Tuesday • 6:30 PM"
            }
        }
