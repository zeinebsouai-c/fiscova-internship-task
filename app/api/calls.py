# FastAPI router with endpoints

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app import models, schemas, services
from typing import List, Optional
from app.database import get_db
from app.services.call_service import create_call_from_transcript, get_calls

router = APIRouter()

@router.post("/intake/call", response_model=schemas.CallResponse, status_code=201)
def intake_call(intake: schemas.CallIntakeRequest, db: Session = Depends(get_db)):
    # Checking for duplicate call_id
    existing = db.query(models.Call).filter(models.Call.call_id == intake.call_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="call_id already exists")
    call = create_call_from_transcript(db, intake)
    return call

@router.get("/calls", response_model=List[schemas.CallResponse])
def list_calls(
    intent: Optional[schemas.IntentEnum] = Query(None),
    urgency: Optional[schemas.UrgencyEnum] = Query(None),
    callback_requested: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    filters = schemas.CallFilterParams(
        intent=intent,
        urgency=urgency,
        callback_requested=callback_requested
    )
    calls = get_calls(db, filters)
    return calls