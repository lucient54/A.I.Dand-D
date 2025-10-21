# api/prompt_builder.py
import json
from typing import Any, Dict, List, Optional

SYSTEM_PROMPT_TEMPLATE = """
You are Ardent, an expert AI Dungeon Master for a fantasy tabletop campaign.
You should describe scenes vividly, react to player actions fairly, and produce a structured JSON output EXACTLY matching the schema.

Rules:
- Never reveal dice rolls; simulate randomness internally.
- Never control player characters' decisions.
- Keep a consistent fantasy tone.
- Output valid JSON only (no commentary).

Schema:
{schema}
""".strip()

def build_system_prompt(schema: str) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(schema=schema)

def build_turn_prompt(world_state: Dict[str, Any],
                      last_narration: Optional[str],
                      recent_dm_notes: Optional[str],
                      player_actions: List[Dict[str, Any]],
                      schema: str) -> str:
    prompt_parts = []
    prompt_parts.append("CONTEXT (World State):")
    prompt_parts.append(json.dumps(world_state, ensure_ascii=False, indent=2))
    prompt_parts.append("\nLAST TURN (Narration Summary):")
    prompt_parts.append(json.dumps(last_narration or "", ensure_ascii=False))
    prompt_parts.append("\nRECENT DM NOTES:")
    prompt_parts.append(json.dumps(recent_dm_notes or "", ensure_ascii=False))
    prompt_parts.append("\nPLAYER ACTIONS (This Turn):")
    prompt_parts.append(json.dumps(player_actions, ensure_ascii=False, indent=2))
    prompt_parts.append("\nINSTRUCTIONS:")
    prompt_parts.append("Based on the current world state and player actions, continue the story.")
    prompt_parts.append("- Update narration and dialogue to reflect the results of these actions.")
    prompt_parts.append("- If combat is triggered or ongoing, include a combat section with round results.")
    prompt_parts.append("- Include any relevant skill checks or quest updates.")
    prompt_parts.append("- Update world changes (NPCs, items, locations, etc.).")
    prompt_parts.append("- Offer 2–4 reasonable next choices for players.")
    prompt_parts.append("- Output ONLY the JSON structure matching the schema below; no additional text.")
    prompt_parts.append("\nOUTPUT SCHEMA:")
    prompt_parts.append(schema)
    return "\n\n".join(prompt_parts)
