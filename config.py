import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

    # opcional
    PORT = int(os.getenv("PORT", 8080))