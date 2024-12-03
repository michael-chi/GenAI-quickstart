"""
FastAPI Main entrance point
"""
# Copyright 2024 Google LLC
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

import tomllib
import os
import google.cloud.logging
import traceback

import vertexai

from fastapi import FastAPI,  Response
from fastapi.middleware.cors import CORSMiddleware

from routers.cache import router as cache_router
from routers.npc import router as npc_router
from routers.imagen import router as imagen_router
from routers.scene import router as scene_router

# ----------------------------------------------------------------------------#
# Load configuration file (config.toml) and global configs
TOML_PATH = "config.toml" if os.environ["CONFIG_TOML_PATH"] == "" else os.environ["CONFIG_TOML_PATH"]
with open(TOML_PATH, "rb") as f:
    config = tomllib.load(f)

ALLOWED_PATH = ["/docs", "/openapi.json"]

client = google.cloud.logging.Client(
    project=config["gcp"]["google-project-id"]
)
client.setup_logging()

# TODO: add asset tracking
_USER_AGENT = "cloud-solutions/smart-npc-v1.0"

vertexai.init(
    project=config["gcp"]["google-project-id"],
    location=config["gcp"]["google-default-region"]
)

app = FastAPI(debug=True)

app.include_router(router=imagen_router)
app.include_router(router=cache_router)
app.include_router(router=scene_router)
app.include_router(router=npc_router)

origins = [
    "*"
]

@app.middleware("http")
async def check_auth_token(request, call_next):
    if request.scope['path'] in ALLOWED_PATH:
        return await call_next(request)

    if "X-API-KEY" in request.headers:
        token = request.headers["X-API-KEY"]
    else:
        token = None

    if token is not None:
        print(f"token={token}")
        print("===")
        print(config["gcp"]["api-key"])
        if token != config["gcp"]["api-key"]:
            return Response(status_code=401)
    else:
        return Response(status_code=401)

    response = await call_next(request)
    return response

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
