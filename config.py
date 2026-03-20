import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Token del bot - requerido
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN no está configurado en las variables de entorno")
    
    # Token de Replicate - opcional (útil para tests)
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    
    # Puerto para Render
    PORT = int(os.getenv("PORT", 8080))
    
    # Configuración adicional
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
# ==============================
# DATABASE
# ==============================

DB_FILE = "database.json"

# ==============================
# CRYPTO PAYMENTS (TRON)
# ==============================

TRX_ADDRESS = os.getenv("TRX_ADDRESS", "TU_DIRECCION_TRON")

TRX_PER_USD = float(os.getenv("TRX_PER_USD", "0.12"))

# ==============================
# PLANES DE CREDITOS
# ==============================

PLANS = {
    "basic": {
        "diamonds": 20,
        "usd": 3
    },
    "pro": {
        "diamonds": 50,
        "usd": 5
    },
    "premium": {
        "diamonds": 120,
        "usd": 10
    }
}