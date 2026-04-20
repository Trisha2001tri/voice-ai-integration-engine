from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import json

from router import route_event

app = FastAPI()


class VoiceEvent(BaseModel):
    caller_name: str
    phone: str
    intent: str
    summary: str
    language: str


@app.post("/voice-event")
def handle_voice_event(
    event: VoiceEvent,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        route_event,
        event.dict()
    )

    return {
        "status": "accepted",
        "message": "Event queued for processing"
    }


@app.get("/logs")
def get_logs():
    with open("logs.json", "r") as f:
        return json.load(f)


@app.get("/failures")
def get_failures():
    failures = []

    with open("failures.log", "r") as f:
        for line in f:
            failures.append(json.loads(line))

    return failures


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "voice-ai-integration-engine",
        "time": str(datetime.now())
    }