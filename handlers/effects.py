import os
import logging
import replicate

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not REPLICATE_API_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN no configurado")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)


# =====================================
# PROCESAR FOTO DEL USUARIO
# =====================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        message = update.message

        await message.reply_text("⚡ Procesando imagen con IA...")

        # Obtener foto mayor resolución
        photo = message.photo[-1]
        file = await photo.get_file()

        input_path = "input.jpg"
        await file.download_to_drive(input_path)

        # ===== EJEMPLO EFECTO (UPSCALE GRATIS) =====
        output = replicate_client.run(
            "nightmareai/real-esrgan",
            input={
                "image": open(input_path, "rb"),
                "scale": 2
            }
        )

        image_url = output

        # Enviar resultado
        await message.reply_photo(photo=image_url)

        # limpiar archivo local
        if os.path.exists(input_path):
            os.remove(input_path)

    except Exception as e:
        logger.error(f"Error procesando imagen: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error procesando la imagen."
        )
