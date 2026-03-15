import replicate
import requests


def upscale_image(image_path, output_path):

    output = replicate.run(
        "cjwbw/real-esrgan",
        input={
            "image": open(image_path, "rb"),
            "scale": 2
        }
    )

    img_data = requests.get(output).content

    with open(output_path, "wb") as f:
        f.write(img_data)