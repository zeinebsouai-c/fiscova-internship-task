# this orchestrates extraction and database operations

from sqlalchemy.orm import Session
from app import models, schemas
from app.services import extraction
from datetime import datetime, timezone

def create_call_from_transcript(db: Session, intake: schemas.CallIntakeRequest):
    intent = extraction.extract_intent(intake.transcript)
    urgency = extraction.extract_urgency(intake.transcript)
    client_number = extraction.extract_client_number(intake.transcript)
    requested_action = extraction.extract_requested_action(intake.transcript)
    callback_requested = extraction.extract_callback_requested(intake.transcript)
    preferred_callback_time = extraction.extract_preferred_callback_time(intake.transcript)

    db_call = models.Call(
        call_id=intake.call_id,
        raw_transcript=intake.transcript,
        intent=intent,
        urgency=urgency,
        client_number=client_number,
        requested_action=requested_action,
        callback_requested=callback_requested,
        preferred_callback_time=preferred_callback_time,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call

def get_calls(db: Session, filters: schemas.CallFilterParams):
    query = db.query(models.Call)
    if filters.intent:
        query = query.filter(models.Call.intent == filters.intent)
    if filters.urgency:
        query = query.filter(models.Call.urgency == filters.urgency)
    if filters.callback_requested is not None:
        query = query.filter(models.Call.callback_requested == filters.callback_requested)
    return query.all()

