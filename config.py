import os
from dotenv import load_dotenv

# cargar .env solo si existe (local)
load_dotenv()

def env(key, default=None):
    value = os.getenv(key)
    if value is None:
        return default
    return value

# =========================
# BOT
# =========================
BOT_TOKEN = env("BOT_TOKEN")

# =========================
# REPLICATE
# =========================
REPLICATE_API_TOKEN = env("REPLICATE_API_TOKEN")

# =========================
# APP CONFIG
# =========================
DEFAULT_LANGUAGE = env("DEFAULT_LANGUAGE", "es")
REQUIRED_CHANNEL = env("REQUIRED_CHANNEL", "false").lower() == "true"
CHANNEL_LINK = env("CHANNEL_LINK", "")
GROUP_LINK = env("GROUP_LINK", "")

# =========================
# STORAGE
# =========================
IMAGE_EXPIRE_HOURS = int(env("IMAGE_EXPIRE_HOURS", 48))

# =========================
# RENDER SAFE MODE
# =========================
RENDER = env("RENDER", "true").lower() == "true"