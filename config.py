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