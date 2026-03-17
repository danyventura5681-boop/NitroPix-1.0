from telegram import Update
from telegram.ext import ContextTypes
import os
import uuid
import replicate
import requests

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if not message or not message.photo:
        return

    photo = message.photo[-1]
    file = await photo.get_file()

    input_path = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}.jpg")
    output_path = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}_ai.jpg")

    await file.download_to_drive(input_path)

    await message.reply_text("🧠 Procesando con IA...")

    try:
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

        # 🔥 Stable Diffusion (Replicate)
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e9345",
            input={
                "image": open(input_path, "rb"),
                "prompt": "cinematic avatar portrait, ultra realistic, sharp focus",
            },
        )

        image_url = output[0]

        # descargar resultado IA
        img_data = requests.get(image_url).content
        with open(output_path, "wb") as f:
            f.write(img_data)

    except Exception as e:
        await message.reply_text(f"❌ Error IA: {e}")
        return

    await message.reply_photo(photo=open(output_path, "rb"))

    # limpiar
    try:
        os.remove(input_path)
        os.remove(output_path)
    except:
        pass
