# handlers/effects.py

from telegram import Update
from telegram.ext import ContextTypes
from PIL import Image, ImageFilter
import os
import uuid


TEMP_FOLDER = "temp"


# crear carpeta temporal si no existe
os.makedirs(TEMP_FOLDER, exist_ok=True)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe una foto del usuario, aplica un efecto simple
    y devuelve la imagen procesada.
    """

    message = update.message

    if not message or not message.photo:
        return

    # obtener la mejor calidad de la foto
    photo = message.photo[-1]

    # descargar archivo desde Telegram
    file = await photo.get_file()

    input_path = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.jpg")
    output_path = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}_effect.jpg")

    await file.download_to_drive(input_path)

    # ---- PROCESAMIENTO CON PILLOW ----
    try:
        image = Image.open(input_path)

        # ejemplo de efecto (BLUR)
        image = image.filter(ImageFilter.BLUR)

        image.save(output_path)

    except Exception as e:
        await message.reply_text(f"❌ Error procesando imagen: {e}")
        return

    # enviar imagen procesada
    try:
        await message.reply_photo(photo=open(output_path, "rb"))
    except Exception as e:
        await message.reply_text(f"❌ Error enviando imagen: {e}")

    # limpiar archivos temporales
    try:
        os.remove(input_path)
        os.remove(output_path)
    except:
        pass
