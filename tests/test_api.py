from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app import models
from app.schemas import IntentEnum, UrgencyEnum

client = TestClient(app)

def setup_module(module):
    # Create tables
    models.Base.metadata.create_all(bind=engine)

def teardown_module(module):
    # Drop tables
    models.Base.metadata.drop_all(bind=engine)

def test_intake_call():
    response = client.post("/intake/call", json={
        "call_id": "test001",
        "transcript": "Hello. I have a question. My client number is 123456. Can you call me back tomorrow morning?",
        "call_timestamp": "2026-02-01T12:00:00Z"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["call_id"] == "test001"
    assert data["intent"] == IntentEnum.INQUIRY.value
    assert data["urgency"] == UrgencyEnum.MEDIUM.value
    assert data["client_number"] == "123456"
    assert data["callback_requested"] == True
    assert data["preferred_callback_time"] is not None

def test_duplicate_call_id():
    # First call
    response1 = client.post("/intake/call", json={
        "call_id": "test002",
        "transcript": "This is a complaint. My client number is 654321. Please call me back.",
        "call_timestamp": "2026-02-01T13:00:00Z"
    })
    assert response1.status_code == 201

    # Duplicate call_id
    response2 = client.post("/intake/call", json={
        "call_id": "test002",
        "transcript": "Another call with same ID.",
        "call_timestamp": "2026-02-01T14:00:00Z"
    })
    assert response2.status_code == 400
    assert response2.json()["detail"] == "call_id already exists"

def test_list_calls_filter():
    client.post("/intake/call", json={
        "call_id": "test003",
        "transcript": "I want to give feedback. My client number is 111222. Please call me back asap.",
        "call_timestamp": "2026-02-01T15:00:00Z"
    })
    response = client.get("/calls?urgency=High&callback_requested=true")
    assert response.status_code == 200
    calls = response.json()
    assert any(call["call_id"] == "test003" for call in calls)
