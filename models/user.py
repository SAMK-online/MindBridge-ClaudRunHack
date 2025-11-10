"""
User Model - User profiles with privacy tier control
"""

from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


# Privacy tiers - 4 levels as shown in mockup
class PrivacyTier(str, Enum):
    """
    Privacy tiers control data storage and therapist handoff support.

    This is a KEY differentiator for MindBridge - user controls their data!
    """

    NO_RECORDS = "no_records"
    # Totally private—nothing saved, just this conversation.
    # No data persistence whatsoever
    # Maximum privacy, minimal support
    # Use case: User wants complete anonymity

    YOUR_PRIVATE_NOTES = "your_private_notes"
    # We keep high-level notes while you stay in control of the details.
    # Basic conversation context saved
    # User maintains control over detailed notes
    # Use case: User wants some continuity with privacy control

    ASSISTED_HANDOFF = "assisted_handoff"
    # We'll help connect you to a therapist and smooth the transitions.
    # Platform facilitates therapist introductions
    # Basic handoff support and context sharing
    # Use case: User wants help with therapist matching and transitions

    FULL_SUPPORT = "full_support"
    # AI can stay with you the whole way, keeping helpful notes and reminders.
    # Complete AI assistance and progress tracking
    # Full therapist-to-therapist handoff support
    # Comprehensive data for continuity of care
    # Use case: User wants maximum support and AI guidance


# Main user model
class User(BaseModel):
    """User profile with privacy controls."""

    # Identification
    id: str = Field(..., description="Unique user identifier")
    email: Optional[EmailStr] = Field(None, description="Email (optional based on privacy)")

    # Privacy settings
    privacy_tier: PrivacyTier = Field(
        default=PrivacyTier.YOUR_PRIVATE_NOTES,
        description="Data storage and handoff support level"
    )

    # Demographics (optional based on privacy tier)
    age: Optional[int] = Field(None, ge=13, le=120, description="Age")
    location: Optional[str] = Field(None, description="City/State for resource matching")
    timezone: str = Field(default="America/New_York", description="User timezone")

    # Status
    is_active: bool = Field(default=True, description="Account active status")
    in_crisis: bool = Field(default=False, description="Currently in crisis flag")

    # Therapist matching
    matched_therapist_id: Optional[str] = Field(
        None,
        description="Currently matched therapist"
    )
    awaiting_match: bool = Field(
        default=False,
        description="Waiting for therapist match"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Account creation date"
    )
    last_active: datetime = Field(
        default_factory=datetime.now,
        description="Last activity"
    )

    # Consent flags
    consented_to_data_collection: bool = Field(
        default=False,
        description="Explicitly consented to data collection"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_001",
                "email": "user@example.com",
                "privacy_tier": "full_support",
                "age": 28,
                "location": "New York, NY",
                "is_active": True,
                "in_crisis": False
            }
        }
