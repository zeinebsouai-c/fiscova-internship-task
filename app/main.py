# Assembles the FastAPI app and creates the database tables

from fastapi import FastAPI
from app.database import engine
from app.api import calls
from app import models

# Creating the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fiscova Call Intake API")

app.include_router(calls.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Fiscova Call Intake API!"}