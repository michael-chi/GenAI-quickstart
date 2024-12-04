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
GenAI-Quickstart Chat API Wrapper.
"""

import requests

class quick_start_wrapper():
    """
    GenAI-Quickstart Chat API Wrapper.
    """
    def __init__(self, model_name:str,
                 system_instruction:str):
        """
        Initialize the wrapper
        Args:
            model_name(str): Name of the model, should be "Gemini"
            system_instruction: System prompt.
            host(str): GenAI-Quickstart chat api host url. ex, http://api.genai.svc
        """
        self.system_instruction = system_instruction
        self.model_name = model_name
        self.host = "http://genai-api.genai.svc/genai/chat/"
        self.history = None

    def start_chat(self, history:list[dict]) -> str:
        """
        Start a chat.
        Args:
            history(list[dict]): conversation history
        Retuns:
            Response from the LLM
        """
        self.history = history
        return self

    def send_message(self,
                     query:list[str],
                     generation_config:dict=None,
                     safety_settings:dict=None) -> str:
        """
        Send message to the chat model.
        Args:
            query(str): User's input
            generation_config(dict): generation config.
            safety_settings(dict): safety settings.
        Retuns:
            LLM response.
        """
        request = {
            "prompt": query[0],
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "message_history": self.history,
            "context": self.system_instruction
        }
        response = requests.post(self.host, json = request, timeout=3)
        print(f"** response={response.text}")
        return response.text
