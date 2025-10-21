# api/dm_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class NPCDialogue(BaseModel):
    name: str
    line: str

class Enemy(BaseModel):
    name: str
    hp: int
    status: List[str] = []

class PlayerOutcome(BaseModel):
    player: str
    action: str
    result: Literal["success", "failure", "partial"]

class SkillCheck(BaseModel):
    type: str
    player: str
    difficulty: int
    result: Literal["success", "failure", "critical success", "critical failure"]

class QuestUpdates(BaseModel):
    added: List[str] = []
    completed: List[str] = []

class WorldChanges(BaseModel):
    location: Optional[str] = None
    new_npcs: List[str] = []
    removed_npcs: List[str] = []
    items_gained: List[str] = []
    items_lost: List[str] = []
    status_effects: List[str] = []

class Combat(BaseModel):
    active: bool = False
    enemies: List[Enemy] = []
    round_summary: Optional[str] = None
    player_outcomes: List[PlayerOutcome] = []

class Events(BaseModel):
    combat: Combat = Field(default_factory=Combat)
    skill_checks: List[SkillCheck] = []
    quest_updates: QuestUpdates = Field(default_factory=QuestUpdates)
    world_changes: WorldChanges = Field(default_factory=WorldChanges)

class DMResponse(BaseModel):
    narration: str
    npc_dialogue: List[NPCDialogue] = []
    events: Events = Field(default_factory=Events)
    player_choices: List[str] = []
    dm_notes: Optional[str] = None
