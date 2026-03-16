import os
import replicate
import requests
import tempfile

replicate_client = replicate.Client(
    api_token=os.getenv("REPLICATE_API_TOKEN")
)


def download_image(url: str) -> str:
    response = requests.get(url)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    tmp.write(response.content)
    tmp.close()
    return tmp.name


# ===============================
# FULL HD UPSCALE
# ===============================
def upscale_hd(image_url: str):

    path = download_image(image_url)

    output = replicate_client.run(
        "nightmareai/real-esrgan",
        input={"image": open(path, "rb")}
    )

    return output


# ===============================
# ANIME STYLE
# ===============================
def anime_style(image_url: str):

    path = download_image(image_url)

    output = replicate_client.run(
        "cjwbw/animeganv2",
        input={"image": open(path, "rb")}
    )

    return output


# ===============================
# MANGA STYLE
# ===============================
def manga_style(image_url: str):

    path = download_image(image_url)

    output = replicate_client.run(
        "tencentarc/gfpgan",
        input={"img": open(path, "rb")}
    )

    return output


# ===============================
# ACTION FIGURE
# ===============================
def action_figure(image_url: str):

    path = download_image(image_url)

    output = replicate_client.run(
        "stability-ai/sdxl",
        input={
            "image": open(path, "rb"),
            "prompt": "action figure toy style, studio lighting, detailed plastic figure"
        }
    )

    return output


# ===============================
# CINEMATIC
# ===============================
def cinematic(image_url: str):

    path = download_image(image_url)

    output = replicate_client.run(
        "stability-ai/sdxl",
        input={
            "image": open(path, "rb"),
            "prompt": "cinematic movie portrait, dramatic lighting, ultra realistic"
        }
    )

    return output