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
Imagen Router

Entry points of generating images.

Attributes:
    router (object): FastAPI router object for Imagen
"""

import os
import tomllib
import uuid

from vertexai.preview.vision_models import ImageGenerationModel

from fastapi import APIRouter

from models.imagen import (
    ImagenRequest,
    ImagenResponse
)

from utils.gcs import upload_file

# ----------------------------------------------------------------------------#
# Load configuration file (config.toml) and global configs
TOML_PATH = "config.toml" if os.environ["CONFIG_TOML_PATH"] == "" else os.environ["CONFIG_TOML_PATH"]
with open(TOML_PATH, "rb") as f:
    config = tomllib.load(f)
# ----------------------------------------------------------------------------#

router = APIRouter(prefix="/imagen", tags=["Imagen"])

# ----------------------------------GET---------------------------------------#

# ----------------------------------POST--------------------------------------#
@router.post(
    path="/generate"
)
def ask(req:ImagenRequest) -> ImagenResponse:
    """Generates Images by natural language inputs

    Args:
        req: Description of the image

    Returns:
        Image url
    """
    # vertexai.init(project=project_id, location="us-central1")

    model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

    images = model.generate_images(
        prompt="Generate an image of \n" + req.description,
        number_of_images=1,
        language=config["npc"]["RESPONSE_LANGUAGE"],
        # You can't use a seed value and watermark at the same time.
        add_watermark=True,
        # seed=100,
        aspect_ratio="1:1",
        safety_filter_level="block_few",
        person_generation="allow_adult",
    )
    local_file = f"img/{uuid.uuid4()}.png"
    print("===>>")
    print(images[0].generation_parameters)
    images[0].save(location=local_file, include_generation_parameters=False)

    # Optional. View the generated image in a notebook.
    # images[0].show()
    url = upload_file(local_file=local_file, project=config["gcp"]["google-project-id"], bucket=config["gcp"]["image_upload_gcs_bucket"])
    print(f"{url}")
    return ImagenResponse(url=url)


