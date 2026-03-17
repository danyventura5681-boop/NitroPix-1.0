import os
import replicate
from config import Config

os.environ["REPLICATE_API_TOKEN"] = Config.REPLICATE_API_TOKEN


def generate_image(prompt: str):

    output = replicate.run(
        "stability-ai/sdxl",
        input={
            "prompt": prompt
        }
    )

    return output[0]