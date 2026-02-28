import pika
import json
from fastapi import FastAPI
from typing import Dict

app = FastAPI()
# In-memory "database"
DB: Dict[str, str] = {
    "alice": "PUBLIC"
}

def publish_event(user: str, visibility: str):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost")
    )
    channel = connection.channel()

    channel.queue_declare(queue="visibility_events")

    event = {
        "user": user,
        "visibility": visibility
    }

    channel.basic_publish(
        exchange="",
        routing_key="visibility_events",
        body=json.dumps(event)
    )

    connection.close()

@app.get("/")
def root():
    return {"message": "Primary Service Running"}

@app.get("/db/{user}")
def get_visibility(user: str):
    visibility = DB.get(user)
    if visibility is None:
        return {"error": "User not found"}
    return {"user": user, "visibility": visibility}

@app.post("/set_visibility/{user}/{visibility}")
def set_visibility(user: str, visibility: str):
    if visibility not in ["PUBLIC", "PRIVATE"]:
        return {"error": "Invalid visibility value"}
    
    DB[user] = visibility
    publish_event(user, visibility)
    return {
        "message": "Visibility updated",
        "user": user,
        "visibility": visibility
    }