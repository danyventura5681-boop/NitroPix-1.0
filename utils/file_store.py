import os
import uuid
import requests

BASE_TEMP_DIR = "/tmp/nitropix"


def ensure_temp_dir():
    os.makedirs(BASE_TEMP_DIR, exist_ok=True)


def save_image_from_url(image_url: str) -> str:
    """
    Descarga imagen IA y la guarda temporalmente.
    """

    ensure_temp_dir()

    filename = f"{uuid.uuid4()}.jpg"
    path = os.path.join(BASE_TEMP_DIR, filename)

    response = requests.get(image_url)

    with open(path, "wb") as f:
        f.write(response.content)

    return path