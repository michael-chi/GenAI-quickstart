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

"""LLM operation help class

Wrapper of LLM operations.
"""

import os
import json

from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.preview import generative_models
from vertexai.generative_models import GenerativeModel
from utils.cacheWrapper import CacheFactory
from utils.chatCache import ChatCacheWrapper

EMBEDDING_MODEL_NAME = "text-multilingual-embedding-002"
TEXT_GENERATION_MODEL_NAME = "gemini-1.5-flash-001"
GEMINI_GENERATION_MODEL_NAME = "gemini-1.5-pro-001"
FLASH_MODEL_NAME = "gemini-1.5-flash-002"
PRO_MODEL_NAME= "gemini-1.5-pro-002"

_chat_sessions = None

def text_embedding(
    task_type: str,
    text: str,
    title: str = "",
    model_name: str = EMBEDDING_MODEL_NAME
  ) -> list:
    """Generate text embedding with a Large Language Model.

    Args:
    task_type (str): Task type,
    Please see:
    https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/task-types#supported_task_types

    text (str): input text
    title (str): Optional title of the input text
    model_name (str): Defaults to text-multilingual-embedding-002

    Returns:
        Embeddings
    """
    model = TextEmbeddingModel.from_pretrained(model_name)
    if task_type == "" or task_type is None:
        print("[Info]NO Emgedding Task Type")
        embeddings = model.get_embeddings([text])
    else:
        print("[Info]Using Emgedding Task Type")
        text_embedding_input = TextEmbeddingInput(
            task_type=task_type, title=title, text=text)
        embeddings = model.get_embeddings([text_embedding_input])
    return embeddings[0].values

def invoke_gemini(
        prompt:str,
        parameters=None) -> str:
    """Invoke Gemini-Pro API.

    Args:
        prompt (str): Prompt

    Returns:
        Gemini prediction results.
    """

    if parameters is None:
        parameters = {
            "max_output_tokens": 8192,
            "temperature": 0.2,
            "top_p": 0.8,
        }

    model = generative_models.GenerativeModel("gemini-pro")
    responses = model.generate_content(
        prompt,
        generation_config=parameters,
    )

    return responses.candidates[0].content.parts[0].text

def ask_llm(prompt:str,
            model_name = TEXT_GENERATION_MODEL_NAME,
            generation_configuration=None,
            safety_configuration=None) -> str:
    """Invoke Language Model.

    Args:
        model_name (str): Model name, defaults to "gemini-1.5-flash-001"
        generation_configuration (dict): Generation config
        safety_configuration (dict): Safty config

    Returns:
        Large Language Model prediction results.
    """
    if generation_configuration is None:
        generation_configuration = {
                "max_output_tokens": 8192,
                "temperature": 1,
                "top_p": 0.95,
            }
    if safety_configuration is None:
        safety_configuration = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
        }
    model = GenerativeModel(
        model_name,
    )
    responses = model.generate_content(
        [prompt],
        generation_config=generation_configuration,
        safety_settings=safety_configuration,
        stream=True,
    )
    result_text = ""
    for response in responses:
        result_text += response.text
    if "```" in result_text:
        result_text = result_text.replace("```json", "").replace("```html", "")
        result_text = result_text[0:result_text.index("```") - 1]
    return result_text

def get_chat_history(npc_id:str, speaker_id:str) -> str:
    """Get conversation history

    Args:
        npc_id (str): NPC's unique Id
        speaker_id (dict): Speaker's Id

    Returns:
        Conversation history between the NPC and the player
    """
    global _chat_sessions
    if _chat_sessions is None or _chat_sessions == {}:
        print("*get_chat_history: chat_sessions is None")
        _chat_sessions = {}

    session_id = f"{npc_id.upper()}_{speaker_id.upper()}"
    if session_id in _chat_sessions:
        return _chat_sessions[session_id].history
    else:
        return ""

# def format_session_id(scene_id:str, npc_id:str, player_id:str, session_id:str) -> str:
#     if scene_id == "":
#         session_id = f"{npc_id.upper()}_{player_id.upper()}_{session_id}"
#     else:
#         session_id = f"{scene_id.upper()}_{session_id}"
#     return session_id

# def get_chat_session(scene_id, session_id, npc_id, player_id, config) -> any:
#     cache = CacheFactory(config).get_cache("scene")
#     session = cache.get(
#         format_session_id(
#             scene_id=scene_id,
#             npc_id=npc_id,
#             player_id=player_id,
#             session_id=session_id)
#     )
#     return session

# def set_chat_session(scene_id, session_id, npc_id, player_id, config, chat) -> str:
#     cache = CacheFactory(config).get_cache("scene")
#     key = format_session_id(
#             scene_id=scene_id,
#             npc_id=npc_id,
#             player_id=player_id,
#             session_id=session_id)
#     cache.set(
#         key,
#         chat.history
#     )
#     return key

def multiturn_generate_content(
        npc_id:str,
        background:str,
        query:str,
        speaker_id:str,
        session_id:str,
        config:dict,
        generation_config=None,
        safety_settings=None,
        scene:str=""
    ):
    """Generate Multi-turn response

    Args:
        npc_id (str): NPC's unique Id
        background (str): NPC's background setting
        query (str): Player's input query
        speaker_id (dict): Speaker's Id

    Returns:
        NPC's response to the player's query
    """
    # global _chat_sessions
    chatCache = ChatCacheWrapper(config=config)
    if generation_config is None:
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }

    if safety_settings is None:
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
        }

    # if scene == "":
    #     session_id = f"{npc_id.upper()}_{speaker_id.upper()}_{session_id}"
    # else:
    #     session_id = f"{scene.upper()}_{session_id}"

    # if _chat_sessions is None or _chat_sessions == {}:
    #     _chat_sessions = {}

    # chat = get_chat_session(
    #     scene_id=scene,
    #     session_id=session_id,
    #     npc_id=npc_id,
    #     player_id=speaker_id,
    #     config=config
    # )

    # if chat is not None:
    #     # chat = _chat_sessions[session_id]
    #     print(f"****** retrieve chat from cache:{session_id} ******")
    #     print(os.linesep.join([c.text for c in chat.history]))
    # else:
    history = chatCache.get_chat_session(
        session_id=session_id,
        scene_id=scene,
        npc_id=npc_id,
        player_id=speaker_id
    )
    model = GenerativeModel(
        TEXT_GENERATION_MODEL_NAME,
        system_instruction=[background]
    )

    chat = model.start_chat(history=history)
        
    # _chat_sessions[session_id] = chat

    result = chat.send_message(
      [query],
      generation_config=generation_config,
      safety_settings=safety_settings
    )
    print(f"****** add chat to cache:{session_id} ******")
    chatCache.set_chat_session(
        session_id=session_id,
        scene_id=scene,
        npc_id=npc_id,
        player_id=speaker_id,
        history=chat.history
    )
    return result

def multiturn_generate_content_v2(
        npc_id:str,
        background:str,
        query:str,
        speaker_id:str,
        session_id:str,
        config:dict,
        generation_config=None,
        safety_settings=None,
        scene:str="",
        model_name:str=FLASH_MODEL_NAME
    ):
    """Generate Multi-turn response

    Args:
        npc_id (str): NPC's unique Id
        background (str): NPC's background setting
        query (str): Player's input query
        speaker_id (dict): Speaker's Id

    Returns:
        NPC's response to the player's query
    """
    # global _chat_sessions
    chatCache = ChatCacheWrapper(config=config)
    if generation_config is None:
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }

    if safety_settings is None:
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
        }

    
    history = chatCache.get_chat_session(
        session_id=session_id,
        scene_id=scene,
        npc_id=npc_id,
        player_id=speaker_id
    )
    model = GenerativeModel(
        model_name,
        system_instruction=[background]
    )

    
    chat = model.start_chat(history=history)
        
    # _chat_sessions[session_id] = chat

    result = chat.send_message(
      [query],
      generation_config=generation_config,
      safety_settings=safety_settings
    )
    print(f"****** add chat to cache:{session_id} ******")
    chatCache.set_chat_session(
        session_id=session_id,
        scene_id=scene,
        npc_id=npc_id,
        player_id=speaker_id,
        history=chat.history
    )
    return result, history

def verify_message_syntax(config:dict, player_input:str, npc_response:str, npcs:str, conversation_history:list) -> str:
    history = ""
    if conversation_history is not None and conversation_history != "":
        for turn in conversation_history:
            # history += f"{turn['role']}: {turn['parts']['text']}\n"
            history += turn.text + os.linesep
    if history == "":
        history = "N/A"
    prompt=config["scene"]["NPC_CONVERSATION_REVIEW"].format(
            NPC_CONVERSATION_DIALOGUE_FORMAT=config["scene"]["NPC_CONVERSATION_DIALOGUE_FORMAT"],
            NON_PLAYER_CHARACTERS=npcs,
            PLAYER_INPUT=player_input,
            NPC_RESPONSE=npc_response,
            CONVERSATION_HISTORY=history)
    # prompt=config["scene"]["NPC_CONVERSATION_REVIEW"] + os.linesep + npc_response
    answer = ask_llm(prompt=prompt)
    print(f"* Rewrite: {answer}")
    return answer

def singleturn_generate_content(npc_id:str,
        background:str,
        query:str,
        speaker_id:str,
        generation_config=None,
        safety_settings=None
    ):
    """Generate Multi-turn response

    Args:
        npc_id (str): NPC's unique Id
        background (str): NPC's background setting
        query (str): Player's input query
        speaker_id (dict): Speaker's Id

    Returns:
        NPC's response to the player's query
    """
    global _chat_sessions

    if generation_config is None:
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }

    if safety_settings is None:
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,  # pylint: disable=line-too-long
        }

    final_prompt = f"""
{background}
player: {query}
"""
    
    # print(f"===PROMPT===\n{final_prompt}")
    result = ask_llm(
        prompt=final_prompt,
        generation_configuration=generation_config,
        safety_configuration=safety_settings,
        model_name=TEXT_GENERATION_MODEL_NAME
    )
    print(f"===ANSWER===\n{result}")
    return result