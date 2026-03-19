import logging

logger = logging.getLogger(__name__)


# ==============================
# PROMPTS POR EFECTO
# ==============================

EFFECT_PROMPTS = {
    "anime": "anime style portrait, high quality, detailed face",
    "action_figure": "toy action figure style, studio lighting",
    "manga": "black and white manga illustration",
    "cinematic": "cinematic movie still, dramatic lighting",
}


# ==============================
# OBTENER PROMPT
# ==============================

def get_prompt(effect: str) -> str:
    return EFFECT_PROMPTS.get(effect, EFFECT_PROMPTS["anime"])


# ==============================
# PIPELINE PRINCIPAL
# ==============================

async def process_image(effect: str, image_url: str):
    """
    Aquí luego conectaremos Replicate.
    Por ahora solo estructura.
    """

    prompt = get_prompt(effect)

    logger.info(f"Processing image with effect: {effect}")
    logger.info(f"Prompt: {prompt}")

    # 🔥 aquí irá replicate.run()

    return {
        "status": "processing",
        "effect": effect,
        "prompt": prompt,
    }