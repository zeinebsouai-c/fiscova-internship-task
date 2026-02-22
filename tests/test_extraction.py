import pytest
from datetime import datetime, timedelta, timezone
from app.services.extraction import (
    extract_intent,
    extract_urgency,
    extract_client_number,
    extract_requested_action,
    extract_callback_requested,
    extract_preferred_callback_time
)
from app.schemas import IntentEnum, UrgencyEnum

def test_extract_intent_feedback():
    text = "I want to give feedback about your service."
    assert extract_intent(text) == IntentEnum.FEEDBACK

def test_extract_urgency_high():
    text = "I need help immediately!"
    assert extract_urgency(text) == UrgencyEnum.HIGH

def test_extract_client_number():
    text = "My client number is 123456."
    assert extract_client_number(text) == "123456"

def test_callback_requested():
    text = "Would you please call me back?"
    assert extract_callback_requested(text) == True

def test_preferred_callbacktime_tomorrow_morning():
    text = "Call me back tomorrow morning."
    result = extract_preferred_callback_time(text)
    assert result is not None
    # Check that it's tomorrow at 9 AM
    tomorrow_9am = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    assert result.date() == tomorrow_9am.date()
    assert result.hour == 9