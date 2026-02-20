# pydantic models for request/response validation

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

class IntentEnum(str, Enum):
    INQUIRY = "Inquiry"
    COMPLAINT = "Complaint"
    FEEDBACK = "Feedback"
    OTHER = "Other"

class UrgencyEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class CallIntakeRequest(BaseModel):
    call_id: str = Field(..., min_length=1, description="Unique identifier for the call")
    transcript: str
    call_timestamp: datetime

    @field_validator("call_id")
    @classmethod
    def not_empty(cls, v) -> str:
        if not v or not v.strip():
            raise ValueError("call_id must not be empty")
        return v.strip()
    
class CallResponse(BaseModel):
    id: int
    call_id: str
    raw_transcript: str
    intent: Optional[IntentEnum]
    urgency: Optional[UrgencyEnum]
    client_number: Optional[str]
    requested_action: Optional[str]
    callback_requested: bool
    preferred_callback_time: Optional[datetime]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class CallFilterParams(BaseModel):
    intent: Optional[IntentEnum] = None
    urgency: Optional[UrgencyEnum] = None
    callback_requested: Optional[bool] = None