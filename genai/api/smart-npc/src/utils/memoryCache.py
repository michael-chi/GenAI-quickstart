# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/memorystore/redis/main.py
# https://redis.io/learn/develop/python/fastapi
"""Conversation History Wrapper

Wrapper of cache mechanism.
This implementation uses in-memory cache.
"""

import json

from vertexai.generative_models import GenerativeModel, ChatSession
from utils.cacheWrapper import CacheFactory
from models.npc import NPCMemoryResponse, MemoryEmotion

class NPCMemory:
    def __init__(self, config):
        self.__prefix = "memory"
        self.__cached_memory = CacheFactory(config).get_cache(self.__prefix)

    def __key(self, player:str, npc:str) -> str:
        return f"{player.upper()}-{npc.upper()}"

    def add_memory(self, player:str, npc:str, memory:list[NPCMemoryResponse]) -> None:
        session_key = self.__key(player=player, npc=npc)
        result = self.__cached_memory.get(session_key)
        print("====>>>>>")
        print(type(result))
        print("------")
        print(f"{result}")
        print("<<<<<====")
        if result is None or result == []:
            result = []

        result.extend(memory)

        self.__cached_memory.set(session_key, result)
    
    def get_memory(self, player:str, npc:str) -> list[NPCMemoryResponse]:
        session_key = self.__key(player=player, npc=npc)
        results = self.__cached_memory.get(session_key)


        return results
        # resp = []
        # for result in results:
        #     print("=====>>>>>>")
        #     print(json.dumps(result))
        #     print("<<<<<<=====")
        #     resp.append(
        #         NPCMemoryResponse(
        #             player_id = result["player_id"],
        #             start_time = result["start_time"],
        #             end_time = result["end_time"],
        #             keywords = result["keywords"],
        #             emotion = MemoryEmotion(
        #                 player = result["emotion"]["player"],
        #                 you = result["emotion"]["you"]
        #             ),
        #             relationship_progress = result["relationship_progress"],
        #             potential_interest = result["potential_interest"],
        #             suggested_next_action = result["suggested_next_action"],
        #             other_info = result["other_info"],
        #             summary = result["summary"],
        #         )
        #     )
        # return resp
