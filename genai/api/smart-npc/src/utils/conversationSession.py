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

import datetime

from vertexai.generative_models import GenerativeModel, ChatSession
from utils.cacheWrapper import CacheFactory

class conversationSessions:
    def __init__(self, config):
        self.__cached_conversations = CacheFactory(config).get_cache("conversations")

    def __key(self, player:str, npc:str) -> str:
        return f"{player}-{npc}"

    def add_conversation_session(self, player:str, npc:str, session:any) -> None:
        session_key = self.__key(player=player, npc=npc)
        o = {
            "history": session.history,
            "enable_automatic_function_calling": session.enable_automatic_function_calling,
            "model_name": session.model_name()
        }
        self.__cached_conversations.set(session_key, o)
    
    def get_conversation_session(self, player:str, npc:str) -> any:
        session_key = self.__key(player=player, npc=npc)
        o = self.__cached_conversations.get(session_key)
        return ChatSession(
            model=GenerativeModel(o["model_name"]),
            history=o["history"],
            enable_automatic_function_calling=o["enable_automatic_function_calling"],
        )

    def get_conversation_history(self, player:str, npc:str) -> list[str]:
        session_key = self.__key(player=player, npc=npc)
        conversation_history = self.__cached_conversations.get(session_key)
        if conversation_history is None:
            conversation_history = []

        return conversation_history 

    def append_conversation_history(self, player:str, speaker:str, npc:str, new_turn:str) -> list[str]:
        session_key = self.__key(player=player, npc=npc)
        if player == speaker:
            turn = f"[{datetime.datetime.now()}]player: {new_turn}"
        else:
            turn = f"[{datetime.datetime.now()}]You: {new_turn}"
    
        conversation_history = self.get_conversation_history(player, npc)
        conversation_history.append(turn)
        self.__cached_conversations.set(session_key, conversation_history)

        return conversation_history
