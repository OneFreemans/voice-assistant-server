from fastapi import FastAPI
from datetime import datetime
import json
import os


app = FastAPI(title="Oleg Assistant API")
STATS_FILE = "/tmp/stats.json"


def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {"total_messages": 0, "last_message_time": None}


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/stats")
async def get_stats():
    return load_stats()