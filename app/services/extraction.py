import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from ..schemas import IntentEnum, UrgencyEnum

def extract_intent(transcript: str) -> Optional[IntentEnum]:
    text = transcript.lower()
    if any(word in text for word in ["feedback", "review", "suggestion", "comment", "appreciate", "prefer"]):
        return IntentEnum.FEEDBACK
    elif any (word in text for word in ["complaint", "unhappy", "issue", "problem", "not satisfied", "bad", "worst", "disappointed", "frustrated"]):
        return IntentEnum.COMPLAINT
    elif any(word in text for word in ["question", "inquiry", "ask", "status", "when", "how", "where", "who", "why"]):
        return IntentEnum.INQUIRY
    return IntentEnum.OTHER

def extract_urgency(transcript: str) -> Optional[UrgencyEnum]:
    text = transcript.lower()
    if any(word in text for word in ["asap", "as soon as possible", "immediately", "urgent", "right away", "emergency", "today"]):
        return UrgencyEnum.HIGH
    elif any(word in text for word in ["soon", "later", "tomorrow", "in two days"]):
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

    # Helper to combine a date with a default time (e.g., 9 AM)
    def at_time(date, hour=9, minute=0):
        return datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute))

    # 1. Immediate / urgent
    if re.search(r'\bright now\b|\basap\b|\bimmediately\b', text):
        return now

    # 2. Specific times tomorrow
    if re.search(r'\btomorrow morning\b', text):
        return at_time(now.date() + timedelta(days=1), hour=9)
    if re.search(r'\btomorrow afternoon\b', text):
        return at_time(now.date() + timedelta(days=1), hour=14)
    if re.search(r'\btomorrow evening\b', text):
        return at_time(now.date() + timedelta(days=1), hour=18)

    # 3. Generic tomorrow (default 9 AM)
    if re.search(r'\btomorrow\b', text):
        return at_time(now.date() + timedelta(days=1), hour=9)

    # 4. Today (default 5 PM, or next morning if already past)
    if re.search(r'\btoday\b', text):
        default_today = at_time(now.date(), hour=17)
        if now > default_today:
            return at_time(now.date() + timedelta(days=1), hour=9)
        return default_today

    # 5. Explicit time of day (e.g., "at 4 pm") – assume today, shift if past
    # Require am/pm to avoid ambiguity
    match = re.search(r'at (\d{1,2})(?:\s*(am|pm))', text, re.IGNORECASE)
    if match:
        hour = int(match.group(1))
        meridiem = match.group(2).lower()
        if meridiem == 'pm' and hour < 12:
            hour += 12
        elif meridiem == 'am' and hour == 12:
            hour = 0
        callback = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        # If that time has already passed today, move to tomorrow
        if callback < now:
            callback += timedelta(days=1)
        return callback

    # 6. Next weekdays (e.g., "next monday")
    weekday_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    for day_name, target_weekday in weekday_map.items():
        if re.search(rf'\bnext {day_name}\b', text):
            days_ahead = (target_weekday - now.weekday() + 7) % 7
            if days_ahead == 0:  # today is that day -> next week
                days_ahead = 7
            target_date = now.date() + timedelta(days=days_ahead)
            return at_time(target_date, hour=9)  # default 9 AM

    # 7. Relative in X hours/days/weeks (e.g., "in 2 hours")
    match = re.search(r'\bin (\d+)\s*(hour|hours|day|days|week|weeks)\b', text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit.startswith('hour'):
            delta = timedelta(hours=amount)
        elif unit.startswith('day'):
            delta = timedelta(days=amount)
        elif unit.startswith('week'):
            delta = timedelta(weeks=amount)
        else:
            delta = timedelta(0)
        return now + delta

    # No match
    return None