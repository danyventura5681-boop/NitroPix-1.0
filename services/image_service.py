import requests


def download_image(url: str, output_path: str):
    response = requests.get(url, timeout=30)

    if response.status_code != 200:
        raise Exception("Failed to download image")

    with open(output_path, "wb") as f:
        f.write(response.content)