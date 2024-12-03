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

from utils.cacheWrapper import CacheFactory

class ChatCacheWrapper:

    def __init__(self, config:dict):
        self.__config = config

    def __format_session_id(self, scene_id:str, npc_id:str, player_id:str, session_id:str) -> str:
        if scene_id == "":
            session_id = f"{npc_id.upper()}_{player_id.upper()}_{session_id}"
        else:
            session_id = f"{scene_id.upper()}_{session_id}"
        print(f"* ChatCacheWrapper:session_id={session_id}")
        return session_id

    def get_chat_session(self, scene_id:str, session_id:str, npc_id:str, player_id:str) -> any:
        cache = CacheFactory(self.__config).get_cache("scene")
        history = cache.get(
            self.__format_session_id(
                scene_id=scene_id,
                npc_id=npc_id,
                player_id=player_id,
                session_id=session_id)
        )
        return history

    def set_chat_session(self, scene_id:str, session_id:str, npc_id:str, player_id:str, history:list[str]) -> str:
        cache = CacheFactory(self.__config).get_cache("scene")
        key = self.__format_session_id(
                scene_id=scene_id,
                npc_id=npc_id,
                player_id=player_id,
                session_id=session_id)
        cache.set(
            key,
            history
        )
        return key
