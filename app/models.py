# Defining the SQLAlchemy ORM model

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import enum

Base = declarative_base()

class IntentEnum(str, enum.Enum):
    INQUIRY = "Inquiry"
    COMPLAINT = "Complaint"
    FEEDBACK = "Feedback"
    OTHER = "Other"

class UrgencyEnum(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, unique=True, nullable=False, index=True)
    raw_transcript = Column(Text, nullable=False)
    intent = Column(Enum(IntentEnum), nullable=True)
    urgency = Column(Enum(UrgencyEnum), nullable=True)
    client_number = Column(String, nullable=True)
    requested_action = Column(String, nullable=True)
    callback_requested = Column(Boolean, default=False)
    preferred_callback_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))