"""
FastAPI NPC Request / Response Models
- NPC Conversations
- NPC Knowledge
- NPC Next Actions
"""
# Copyrightll 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pydantic import BaseModel
from typing import Union, Optional

class SearchNPCKnowledgeRequest(BaseModel):
    npc_lore_level: int
    query: str

class Knowledge(BaseModel):
    knowledge: str
    lore_level: int
    score: float

class SearchNPCKnowledgeResponse(BaseModel):
    knowledge: list[Knowledge]

class NPCConversationRequest(BaseModel):
    player_id: str
    npc_id: str
    speaker: str=""
    sentence: str=""
    in_game_time: str=""
    end: Optional[bool]=True

class NPCConversationResponse(BaseModel):
    player_id: str
    npc_id: str
    speaker: str
    sentence: dict
    in_game_time: str
    end: bool

class NPCInfoRequest(BaseModel):
    npc_id: str

class NPCInfoResponse(BaseModel):
    npc_id: str
    background: str
    npc_class: str
    class_level: int
    name: str
    status: str
    lore_level: int

class NPCMemoryRequest(BaseModel):
    player_id: str
    npc_id: str

class MemoryEmotion(BaseModel):
    player: str
    you: str


class NPCMemoryResponse(BaseModel):
    player_id: str
    keywords: list[str] = []
    start_time: str = ""
    end_time: str = ""
    emotion: MemoryEmotion = None
    relationship_progress: str = ""
    potential_interest: str = ""
    suggested_next_action: str = ""
    other_info: list[dict] = []
    summary: str = ""
