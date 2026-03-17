import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

    # opcional
    PORT = int(os.getenv("PORT", 8080))