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

"""
NPC Router

Entry points of NPC related actions.

Attributes:
    router (object): FastAPI router object for NPC actions
"""

import os
import json
import tomllib

from typing import Optional
from fastapi import APIRouter, HTTPException

from utils.cacheWrapper import CacheFactory
from models.npc import (
    NPCInfoResponse
)
from utils.database import DataConnection

from utils.conversationSession import conversationSessions

# ----------------------------------------------------------------------------#
# Load configuration file (config.toml) and global configs
TOML_PATH = "config.toml" if os.environ["CONFIG_TOML_PATH"] == "" else os.environ["CONFIG_TOML_PATH"]
with open(TOML_PATH, "rb") as f:
    config = tomllib.load(f)

_connection = DataConnection(config=config)

# ----------------------------------------------------------------------------#

router = APIRouter(prefix="/npcs", tags=["NPC - Conversations"])

_chatSessions = conversationSessions(config)
__cached_npc = CacheFactory(config).get_cache("npc")
# ----------------------------------GET---------------------------------------#
@router.get(
    path="/get-npc/{npc_id}", response_model=NPCInfoResponse
)
def get_npc(npc_id:str) -> NPCInfoResponse:
    """Get NPC configuration by id

    Args:
        npc_id: unique id of the NPC.

    Returns:
        NPC information object.
    """

    resp = __cached_npc.get(npc_id)
    if resp is not None:
        return resp
    try:
        sql = config["sql"]["QUERY_NPC_BY_ID"].format(npc_id)
        print(f"* SQL={sql}")
        npc = _connection.execute(sql, None)
        for row in npc:
            resp = NPCInfoResponse(
                background = row[1],
                name = row[2],
                npc_class = row[3],
                class_level = row[4],
                npc_id = npc_id,
                status = row[5],
                lore_level = int(row[6])
            )
            __cached_npc.set(npc_id, resp)
            return resp
    except Exception as e:
        raise HTTPException(status_code=400,
                    detail=f"Cloud SQL error: {e}") from e
