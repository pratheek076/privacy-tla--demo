from fastapi import FastAPI
import pika
import json
import threading
import time
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
CACHE = {}

def load_initial_snapshot():
    while True:
        try:
            response = httpx.get("http://primary:8000/db/alice")
            data = response.json()
            CACHE["alice"] = data["visibility"]
            print("Cache updated:", CACHE)
            break
        except:
            print("Primary not ready, retrying...")
            time.sleep(1)

def consume():
    print("Starting RabbitMQ consumer..." )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("rabbitmq")
    )
    channel = connection.channel()

    channel.queue_declare(queue="visibility_events")

    def callback(ch, method, properties, body):
        event = json.loads(body)

        user = event["user"]
        visibility = event["visibility"]
        if visibility == "PRIVATE":
            time.sleep(5)
        else:
            time.sleep(0)

        CACHE[user] = visibility
        print("Cache updated:", CACHE)

    channel.basic_consume(
        queue="visibility_events",
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()

@app.on_event("startup")
def startup_event():
    load_initial_snapshot()

    thread = threading.Thread(target=consume)
    thread.daemon = True
    thread.start()

@app.get("/cache/{user}", response_class=HTMLResponse)
def get_cache(user: str):
    visibility = CACHE.get(user, "PUBLIC")

    if visibility == "PUBLIC":
        return """
        <div id="messageBox">
            <p class="public">
                Hello, I am Alice. My message is visible.
            </p>
        </div>
        """

    return """
    <div id="messageBox">
        <p class="private">
            Message is hidden (PRIVATE).
        </p>
    </div>
    """