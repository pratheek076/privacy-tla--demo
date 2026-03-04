import pika
import httpx
import json
from fastapi import FastAPI
from typing import Dict
from fastapi.responses import HTMLResponse


app = FastAPI()
# In-memory "database"
DB: Dict[str, str] = {
    "alice": "PRIVATE"
}

def publish_event(user: str, visibility: str):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("rabbitmq")
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

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("ui/index.html") as f:
        return f.read()

@app.get("/cache_proxy/{user}", response_class=HTMLResponse)
def proxy_cache(user: str):
    response = httpx.get(f"http://cache:8001/cache/{user}")
    return response.text