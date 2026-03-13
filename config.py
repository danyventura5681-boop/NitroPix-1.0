import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
TRX_ADDRESS = "TK2K6W7vFehHLB6eQ9CPPjcJ1E6ErCu12Y"

PLANS = {
    "20": {"usd": 5, "diamonds": 20},
    "50": {"usd": 10, "diamonds": 50},
    "100": {"usd": 15, "diamonds": 100}
}

TRX_PER_USD = 10
DATABASE_URL = "sqlite:///nitropix.db"