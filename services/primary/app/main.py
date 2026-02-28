from fastapi import FastAPI
from typing import Dict

app = FastAPI()
# In-memory "database"
DB: Dict[str, str] = {
    "alice": "PUBLIC"
}

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
    return {
        "message": "Visibility updated",
        "user": user,
        "visibility": visibility
    }