"""
FastAPI NPC chat in a scence Request / Response Models
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

class NPCSceneConversationRequest(BaseModel):
    player_id: str
    npc_id: str=""
    sentence: str=""
    in_game_time: str=""
    scene_id: str=""
    session_id: str

class NPCSceneConversationResponse(BaseModel):
    player_id: str
    npc_ids: list[str]=[]
    scene_id: str=""
    sentence: str
    in_game_time: str=""
    session_id: str

class Scene(BaseModel):
    scene_id :str
    scene: str
    npc_ids: list[str]
    goal:str
    status: str
    knowledge: str
