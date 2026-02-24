# Fiscova Call Intake Service

A backend service for processing phone call transcripts, extracting structured information, and storing it for retrieval.

Built with **FastAPI, SQLAlchemy, and SQLite**.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Setup & Installation](#setup--installation)
  - [Local Development](#local-development)
  - [Running with Docker](#running-with-docker)
- [Testing](#testing)
- [Assumptions & Design Choices](#assumptions--design-choices)
- [Future Improvements](#future-improvements)

---

## Tech Stack

- Python 3.11  
- FastAPI  
- SQLAlchemy  
- SQLite  
- Pydantic  
- pytest  
- Docker  

---

## Features

- Accept raw call transcripts via `POST /intake/call`
- Extract structured information from transcripts (intent, urgency, client_number, requested_action, callback_requested, preferred_callback_time)
- Store processed calls in SQLite
- Retrieve calls with filters via `GET /calls`
- Duplicate detection via `call_id`
- Unit tests
- Docker support with persistent database volume

---

# Setup & Installation

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/zeinebsouai-c/fiscova-internship-task.git
cd fiscova-internship-task
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Linux / macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

Then open:

```
http://localhost:8000/docs
```

---

## Running with Docker

Make sure Docker Desktop is running.

Build and start the container:

```bash
docker-compose up --build
```

The API will be available at:

```
http://localhost:8000
```

The `calls.db` file is mounted via a Docker volume so data persists between container restarts.

---

### SETUP verification

Once the container is running, open another terminal and test the API:

```bash
curl http://localhost:8000/calls
```
 
If you see an empty list ([]) or your previously added calls, the service is working.

You can also add a new call via `curl`:

```bash
curl -X POST http://localhost:8000/intake/call \
  -H "Content-Type: application/json" \
  -d '{"call_id":"test-123","transcript":"Hello, this is a test.","call_timestamp":"2026-02-23T12:00:00Z"}'
```
(call_id should be unique if testing multiple times.)

Then refresh `curl http://localhost:8000/calls` to see the new entry in the container.

Alternatively, you can use the interactive Swagger UI at http://localhost:8000/docs to add entries.

## Endpoints

### POST `/intake/call`

Request body:

```json
{
  "call_id": "unique-string",
  "transcript": "Hello, this is Müller...",
  "call_timestamp": "2026-02-24T12:00:00Z"
}
```

Response (201 Created):

```json
{
  "id": 1,
  "call_id": "unique-string",
  "raw_transcript": "...",
  "intent": "inquiry",
  "urgency": "medium",
  "client_number": "48291",
  "requested_action": "Could someone call me back...",
  "callback_requested": true,
  "preferred_callback_time": "2026-02-25T09:00:00",
  "created_at": "2026-02-24T12:00:00"
}
```

---

### GET `/calls`

Optional query parameters:

- `intent` → inquiry | complaint | feedback | other  
- `urgency` → low | medium | high  
- `callback_requested` → true | false  

Example:

```
GET /calls?intent=inquiry&callback_requested=true
```

---

# Testing

Run:

```bash
pytest tests/ -v
```

---

# Trade-offs & Design Decisions

### Extraction Logic
- Rule‑based instead of ML: Chosen for speed and simplicity, more suitable for the task’s scope but less robust to varied phrasing.
- Intent classification: Simple keyword matching works for examples but may overlap or miss synonyms.
- Client number: Regex covers common patterns but may miss numbers without keywords or with fewer than 4 digits.
- Requested action: Returns the first sentence containing request phrases, ignores multi‑sentence requests or unusual punctuation.
- Callback time parsing: Ordered rules with default times (9 AM, 2 PM, 5 PM) cover common phrases but miss many variants. “Today” defaults to 5 PM (or next morning if past). “At 4 pm” requires AM/PM to avoid ambiguity. All times stored as UTC (caller timezone not considered).

### Project Structure & Technology
- SQLite: Lightweight, file‑based, no server setup; trades concurrency and advanced features for simplicity.
- Docker: Containerisation with host‑mounted calls.db ensures data persistence.
- Testing: Focused on critical extraction functions and API endpoints; not exhaustive but provides good coverage for a demo.
- Code organisation: Modular separation (models, schemas, services, API).

These choices keep the project focused, understandable, and easy to extend.
---

# Future Improvements

- Replace rule-based parsing with an NLP model.
- Add pagination: Limiting results on GET /calls to avoid overwhelming responses.
- Add authentication: Securing the API with API keys or login to prevent unauthorised access.
- Improve logging & monitoring: Tracking errors and performance for easier debugging and maintenance.
