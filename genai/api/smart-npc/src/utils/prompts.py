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

"""
Prompt Management
"""

def get_conversation_prompt(with_goal:bool, config:dict) -> str:
    generation_rules = config["scene"]["NPC_CONVERSATION_RULES"]
    link_syntax = config["scene"]["NPC_CONVERSATION_DIALOGUE_FORMAT"]

    if with_goal:
        template = config["scene"]["NPC_CONVERSATION_SCENCE_GOAL_TEMPLATE"]
    else:
        template = config["scene"]["NPC_CONVERSATION_SCENCE_NO_GOAL_TEMPLATE"]

    prompt = template.replace(
        "{NPC_CONVERSATION_DIALOGUE_FORMAT}",
        link_syntax).replace(
            "{NPC_CONVERSATION_RULES}",
            generation_rules)

    return prompt
