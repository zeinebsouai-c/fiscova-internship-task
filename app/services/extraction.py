import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from ..schemas import IntentEnum, UrgencyEnum

def extract_intent(transcript: str) -> Optional[IntentEnum]:
    text = transcript.lower()
    if any(word in text for word in ["feedback", "review"]):
        return IntentEnum.FEEDBACK
    elif any (word in text for word in ["complaint", "unhappy", "issue", "problem"]):
        return IntentEnum.COMPLAINT
    elif any(word in text for word in ["question", "inquiry", "ask", "status", "when", "how"]):
        return IntentEnum.INQUIRY
    return IntentEnum.OTHER

def extract_urgency(transcript: str) -> Optional[UrgencyEnum]:
    text = transcript.lower()
    if any(word in text for word in ["asap", "as soon as possible", "immediately", "urgent", "right away", "now", "emergency", "today"]):
        return UrgencyEnum.HIGH
    elif any(word in text for word in ["soon", "later", "tomorrow"]):
        return UrgencyEnum.MEDIUM
    return UrgencyEnum.LOW

def extract_client_number(transcript: str) -> Optional[str]:
    patterns = [
        r'client\s*(?:number|id)?[^0-9]*(\d{4,})',
        r'customer\s*(?:number|id)?\s*[:\s]*(\d{4,})',
        r'account\s*(?:number|id)?\s*[:\s]*(\d{4,})',
    ]
    for pat in patterns:
        match = re.search(pat, transcript, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def extract_requested_action(transcript: str) -> Optional[str]:
    sentences = re.split(r'[.?!]', transcript)
    for sent in sentences:
        if re.search(r'(could you|please|I need|I wouldlike)', sent, re.IGNORECASE):
            return sent.strip()
    return None

def extract_callback_requested(transcript: str) -> bool:
    return "call me back" in transcript.lower() or "callback" in transcript.lower()

def extract_preferred_callback_time(transcript: str) -> Optional[datetime]:
    text = transcript.lower()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if "tomorrow" in text:
        return (now + timedelta(days=1)).date()
    elif "today" in text:
        return now.date()
    elif "right now" in text or "asap" in text or "immediately" in text:
        return now
    elif "next week" in text:
        return now + timedelta(weeks=1)
    elif "tomorrow morning" in text:
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    elif "tomorrow afternoon" in text:
        return (now + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
    elif "next monday" in text:
        days_ahead = (0 - now.weekday() + 7) % 7
        return now + timedelta(days=days_ahead)
    elif "next tuesday" in text:
        days_ahead = (1 - now.weekday() + 7) % 7
        return now + timedelta(days=days_ahead)
    elif "next wednesday" in text:
        days_ahead = (2 - now.weekday() + 7) % 7
        return now + timedelta(days=days_ahead)
    elif "next thursday" in text:
        days_ahead = (3 - now.weekday() + 7) % 7
        return now + timedelta(days=days_ahead)
    elif "next friday" in text:
        days_ahead = (4 - now.weekday() + 7) % 7
        return now + timedelta(days=days_ahead)
    return None

