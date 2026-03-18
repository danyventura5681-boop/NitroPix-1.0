import os
import replicate
import requests
import tempfile

# ===============================
# CLIENT SETUP
# ===============================

REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not REPLICATE_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN not found in environment variables")

replicate_client = replicate.Client(api_token=REPLICATE_TOKEN)


# ===============================
# HELPERS
# ===============================

def download_image(url: str) -> str:
    """Download image from URL into a temporary file."""
    response = requests.get(url, timeout=30)

    if response.status_code != 200:
        raise Exception("Failed to download image")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    tmp.write(response.content)
    tmp.close()

    return tmp.name


def run_model(model: str, input_data: dict):
    """Run replicate model safely."""
    try:
        output = replicate_client.run(model, input=input_data)
        return output
    except Exception as e:
        raise Exception(f"Replicate error: {str(e)}")


def process_image(image_url: str, model: str, input_builder):
    """
    Generic processor:
    - downloads image
    - runs model
    - cleans temp file
    """
    path = download_image(image_url)

    try:
        with open(path, "rb") as img:
            output = run_model(model, input_builder(img))
        return output

    finally:
        if os.path.exists(path):
            os.remove(path)


# ===============================
# FULL HD UPSCALE
# ===============================

def upscale_hd(image_url: str):
    return process_image(
        image_url,
        "nightmareai/real-esrgan",
        lambda img: {"image": img},
    )


# ===============================
# ANIME STYLE
# ===============================

def anime_style(image_url: str):
    return process_image(
        image_url,
        "cjwbw/animeganv2",
        lambda img: {"image": img},
    )


# ===============================
# MANGA STYLE
# ===============================

def manga_style(image_url: str):
    return process_image(
        image_url,
        "tencentarc/gfpgan",
        lambda img: {"img": img},
    )


# ===============================
# ACTION FIGURE
# ===============================

def action_figure(image_url: str):
    return process_image(
        image_url,
        "stability-ai/sdxl",
        lambda img: {
            "image": img,
            "prompt": "action figure toy style, studio lighting, detailed plastic figure",
        },
    )


# ===============================
# CINEMATIC
# ===============================

def cinematic(image_url: str):
    return process_image(
        image_url,
        "stability-ai/sdxl",
        lambda img: {
            "image": img,
            "prompt": "cinematic movie portrait, dramatic lighting, ultra realistic",
        },
    )