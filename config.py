import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    GROUP_LINK = os.getenv('GROUP_LINK', 'https://t.me/+_46_k-WxFRZkYzcx')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '8248755019').split(',') if id]
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    PORT = int(os.getenv('PORT', 8080))
    
    # Costos de efectos
    EFFECT_COSTS = {
        'avatar': 2,
        'figura': 2,
        'dibujo': 1,
        'artistico': 2
    }
    
    # Modelos de IA
    AI_MODELS = {
        'avatar': 'stabilityai/stable-diffusion-xl-base-1.0',
        'figura': 'dreamshaper/dreamshaper_8',
        'dibujo': 'runwayml/stable-diffusion-v1-5',
        'artistico': 'stabilityai/stable-diffusion-2-1'
    }

config = Config()