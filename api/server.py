# api/server.py
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Any, Dict, List
from dm_schema import DMResponse
from prompt_builder import build_system_prompt, build_turn_prompt
from openai_client import call_openai_chat
from redis_manager import get_session_state, set_session_state, get_dm_notes, set_dm_notes, get_last_narration, set_last_narration

# Load schema string using Pydantic, pretty
SCHEMA_STR = DMResponse.schema_json(indent=2)
SYSTEM_PROMPT_FULL = build_system_prompt(SCHEMA_STR)

app = FastAPI(title="AI DM Backend")

class PlayerActionPayload(BaseModel):
    player_id: str
    action: str
    timestamp: str
    meta: Dict[str, Any] = {}

def build_prompt_for_turn(session_state: dict, last_narration: str, dm_notes: str, actions: List[dict]) -> str:
    return build_turn_prompt(
        world_state=session_state,
        last_narration=last_narration,
        recent_dm_notes=dm_notes,
        player_actions=actions,
        schema=SCHEMA_STR
    )

@app.post("/v1/session/{session_id}/action")
async def submit_action(session_id: str, payload: PlayerActionPayload, background_tasks: BackgroundTasks):
    # 1) fetch session state
    world_state = get_session_state(session_id)
    if not world_state:
        raise HTTPException(status_code=404, detail="Session not found")

    last_narration = get_last_narration(session_id)
    dm_notes = get_dm_notes(session_id)

    actions = [payload.dict()]
    prompt_user = build_prompt_for_turn(world_state, last_narration, dm_notes, actions)

    # 2) call OpenAI
    try:
        raw = call_openai_chat(SYSTEM_PROMPT_FULL, prompt_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI call failed: {e}")

    # 3) try to parse and validate
    parsed_json = None
    dm_response = None
    try:
        parsed_json = json.loads(raw)
        dm_response = DMResponse(**parsed_json)
    except Exception:
        # attempt a simple repair pass by asking the model to reformat only
        repair_prompt = f"Your last output was not valid JSON. Please reformat ONLY the JSON object to match this schema:\n{SCHEMA_STR}\n\nPrevious output:\n{raw}"
        try:
            raw2 = call_openai_chat(SYSTEM_PROMPT_FULL, repair_prompt)
            parsed_json = json.loads(raw2)
            dm_response = DMResponse(**parsed_json)
        except Exception:
            # fallback
            fallback = DMResponse(
                narration="A murmur of uncertainty passes over the scene; the story continues, though some details are unclear.",
                npc_dialogue=[],
                events={},
                player_choices=["Proceed cautiously"],
                dm_notes="Fallback used: model output invalid and repair failed."
            )
            return fallback.dict()

    # 4) apply world changes to session state (simple merge)
    wc = dm_response.events.world_changes
    if wc.location:
        world_state["location"] = wc.location
    if wc.new_npcs:
        world_state.setdefault("npcs", []).extend(wc.new_npcs)
    if wc.removed_npcs:
        existing_npcs = world_state.get("npcs", [])
        world_state["npcs"] = [n for n in existing_npcs if n not in wc.removed_npcs]
    if wc.items_gained:
        world_state.setdefault("items", []).extend(wc.items_gained)
    if wc.items_lost:
        current_items = world_state.get("items", [])
        world_state["items"] = [i for i in current_items if i not in wc.items_lost]
    if wc.status_effects:
        world_state.setdefault("status_effects", []).extend(wc.status_effects)

    # 5) persist
    set_session_state(session_id, world_state)
    if dm_response.dm_notes:
        set_dm_notes(session_id, dm_response.dm_notes)
    set_last_narration(session_id, dm_response.narration)

    # Return the DMResponse dict (FastAPI will JSON-serialize)
    return dm_response.dict()
