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
import tomllib

from fastapi import APIRouter, HTTPException

from utils.cacheWrapper import CacheFactory
from utils.prompts import get_conversation_prompt
from models.scence import (
    NPCSceneConversationRequest,
    NPCSceneConversationResponse,
    Scene
)

from utils.cacheWrapper import CacheWrapper
from utils.database import DataConnection
from utils.llm import multiturn_generate_content, verify_message_syntax, multiturn_generate_content_v2, FLASH_MODEL_NAME, PRO_MODEL_NAME
from utils.conversationSession import conversationSessions
from routers.npc import get_npc

router = APIRouter(prefix="/scenes", tags=["SCENCE - Conversations"])

# ----------------------------------------------------------------------------#
# Load configuration file (config.toml) and global configs
TOML_PATH = "config.toml" if os.environ["CONFIG_TOML_PATH"] == "" else os.environ["CONFIG_TOML_PATH"]
with open(TOML_PATH, "rb") as f:
    config = tomllib.load(f)

# ----------------------------------Variables and Functions---------------------------------------#
cached_scene = CacheFactory(config).get_cache("scene")
cached_conv_example = CacheFactory(config).get_cache("conv_example")

def get_conversation_example(scene_id:str) -> str:
    conv = cached_conv_example.get(scene_id)
    if conv is None or conv == "":
        with open("data/conversation_exempl.txt", "r", encoding="utf-8") as f:
            conv = f.read()
    return conv

def substring_occurence(test_str:str, test_sub:str) -> int:
    occurence = len(test_str.split(test_sub)) - 1
    print(f"* substring_occurence={occurence}")

    return occurence

# ----------------------------------GET---------------------------------------#
@router.get(
    path="/{scene_id}"
)
def get_scence(scene_id:str) -> Scene:
    scene = cached_scene.get(scene_id)
    print(f"* get_scene:{scene}")
    if scene is not None:
        return scene
    try:
        connection = DataConnection(config=config)

        sql = config["sql"]["QUERY_SCENE"]
        print(f"** sql={sql}")
        rows = connection.execute(sql, {
            "scene_id": scene_id
        })
        for row in rows:
            resp = Scene(
                scene_id=row[0],
                scene=row[1],
                goal=row[3],
                npc_ids=[n.strip() for n in f"{row[4]}".split(",")],
                status=row[2],
                knowledge=row[5]
            )
            cached_scene.set(scene_id, resp)
            return resp
    except Exception as e:
        raise HTTPException(status_code=400,
                    detail=f"Error: {e}") from e

# ----------------------------------POST---------------------------------------#
@router.post(
    path="/chat"
)
def chat(req:NPCSceneConversationRequest) -> NPCSceneConversationResponse:
    """Generates NPC responses

    Args:
        req: Player's input query.

    Returns:
        NPC's response to the player's inpput.
    """

    print(f"* chat.sentence={req.sentence}")
    if req.sentence.startswith("[CHAR") == False:
        req.sentence = f"[CHAR({req.player_id}:{req.npc_id})]{req.sentence}"
        print(f"* Reformated sentence: {req.sentence}")

    if req.scene_id is not None and req.scene_id != "":
        scene = get_scence(scene_id=req.scene_id)
        if scene is None:
            raise HTTPException(status_code=400,
                                detail=f"Scene not found:{req.scene_id}")
    npcs = []
    for npc in scene.npc_ids if scene.npc_ids is not None else []:
        npc = get_npc(npc_id=npc)
        if npc is not None:
            npcs.append(npc)
        else:
            raise HTTPException(status_code=400,
                                detail=f"NPC not found:{req.npc_id}")
    
    for npc in scene.knowledge.split(",") if scene.knowledge is not None and scene.knowledge != "" else []:
        npc = get_npc(npc_id=npc)
        if npc is not None:
            npcs.append(npc)
        else:
            raise HTTPException(status_code=400,
                                detail=f"NPC not found:{req.npc_id}")
    # TODO: No Knowledge at the moment
    # max_lore_level = max([npc.lore_level for npc in npcs])
    # knowledge = search_knowledge(SearchNPCKnowledgeRequest(
    #     npc_lore_level = max_lore_level,
    #     query = req.sentence
    # ))

    # TODO: Let's revist how to fetch quests in this scene
    # quests = search_quest(
    #     npc_id=req.npc_id
    # )

    # language_code = config["npc"]["RESPONSE_LANGUAGE"]

    # TODO: In this case, we do not need the player information.
    #       Because all charachter information, including the main character inforamtion
    #       is listed with other characters in the prompt.
    # player = get_player_info()
    npc_in_the_scene = ",".join([id for id in scene.npc_ids if id != "Erika"])
    print(f"*npc_in_the_scene={npc_in_the_scene}")
    print(f"*scene.knowledge={scene.knowledge}")
    if scene.goal != "" and scene.goal != "NA":
        prompt = get_conversation_prompt(with_goal=True, config=config)
        prompt = prompt.format(
                CHARACTER_BACKGROUND=f"{os.linesep}".join([npc.background for npc in npcs]),
                CONVERSATION_EXAMPLE=get_conversation_example(req.scene_id),
                CURRENT_SCENE=get_scence(req.scene_id).scene,
                SCENC_GOAL=scene.goal,
                NON_PLAYER_CHARACTERS=npc_in_the_scene)
    else:
        prompt = get_conversation_prompt(with_goal=False, config=config)
        prompt = prompt.format(
                CHARACTER_BACKGROUND=f"{os.linesep}".join([npc.background for npc in npcs]),
                CONVERSATION_EXAMPLE=get_conversation_example(req.scene_id),
                CURRENT_SCENE=get_scence(req.scene_id).scene,
                NON_PLAYER_CHARACTERS=npc_in_the_scene)
    
    answer, history = multiturn_generate_content_v2(
        npc_id=req.npc_id,
        background=prompt,
        query=req.sentence,
        speaker_id=req.player_id,
        session_id=req.session_id,
        config=config,
        scene=req.scene_id,
        model_name=FLASH_MODEL_NAME
    )

    # print(f"=== PROMPT ===\n{prompt}\n==============")
    json_answer_text = answer.candidates[0].content.parts[0].text.replace("```json", "").replace("```", "") # pylint: disable=line-too-long
    print(f"==RESULT==\n{json_answer_text}\n=======")
    json_answer_text = verify_message_syntax(
        config=config,
        player_input=req.sentence,
        npc_response=json_answer_text,
        npcs=npc_in_the_scene,
        conversation_history=history
    )
    occurence = substring_occurence(test_str=json_answer_text, test_sub="[CHAR(")

    if occurence > 1:
        json_answer_text = json_answer_text.replace("[CHAR(", os.linesep + "[CHAR(")

    json_answer_text = json_answer_text.replace("\\n", "")

    if "[NARR" in json_answer_text and os.linesep + "[NARR" not in json_answer_text:
        json_answer_text = json_answer_text.replace("[NARR", os.linesep + "[NARR")
    commands = json_answer_text.split(os.linesep)
    commands = list(filter(None, commands))
    result_text = ""
    for command in commands:
        if command.startswith("[CHAR(") or command.startswith("[NARR("):
            result_text += command + os.linesep


    return NPCSceneConversationResponse(
        player_id=req.player_id,
        npc_id=",".join(scene.npc_ids),
        scene_id=req.scene_id,
        sentence=json_answer_text, # refined_text, # 
        session_id=req.session_id
    )
