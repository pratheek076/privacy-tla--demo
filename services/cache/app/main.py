from fastapi import FastAPI
import pika
import json
import threading
import time

app = FastAPI()

CACHE = {}

def consume():
    print("Starting RabbitMQ consumer..." )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters("localhost")
    )
    channel = connection.channel()

    channel.queue_declare(queue="visibility_events")

    def callback(ch, method, properties, body):
        event = json.loads(body)

        user = event["user"]
        visibility = event["visibility"]
        if visibility == "PUBLIC":
            time.sleep(15)
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
    thread = threading.Thread(target=consume)
    thread.daemon = True
    thread.start()

@app.get("/cache/{user}")
def get_cache(user: str):
    visibility = CACHE.get(user)
    if visibility is None:
        return {"error": "User not found in cache"}
    return {"user": user, "visibility": visibility}