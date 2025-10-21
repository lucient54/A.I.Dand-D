# api/redis_manager.py
import os
import json
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_session_state(session_id: str) -> dict:
    raw = r.get(f"session:{session_id}:state")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}

def set_session_state(session_id: str, state: dict):
    r.set(f"session:{session_id}:state", json.dumps(state))

def get_dm_notes(session_id: str) -> str:
    return r.get(f"session:{session_id}:dm_notes") or ""

def set_dm_notes(session_id: str, notes: str):
    r.set(f"session:{session_id}:dm_notes", notes)

def get_last_narration(session_id: str) -> str:
    return r.get(f"session:{session_id}:last_narration") or ""

def set_last_narration(session_id: str, narration: str):
    r.set(f"session:{session_id}:last_narration", narration)
