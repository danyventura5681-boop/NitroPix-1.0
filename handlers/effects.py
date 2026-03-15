import os
import uuid
from PIL import Image, ImageFilter, ImageEnhance
from telegram import Update
from telegram.ext import ContextTypes

from database import get_user, deduct_diamond

TEMP_FOLDER = "temp"


def apply_effect(image, effect):

    if effect == "blur":
        return image.filter(ImageFilter.GaussianBlur(6))

    elif effect == "sharpen":
        return image.filter(ImageFilter.SHARPEN)

    elif effect == "bw":
        return image.convert("L")

    elif effect == "contrast":
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.6)

    elif effect == "bright":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.5)

    return image


async def process_effect(update: Update, context: ContextTypes.DEFAULT_TYPE, effect_name: str, cost: int):

    user = update.effective_user
    user_id = user.id

    db_user = get_user(user_id)

    if not db_user:
        await update.message.reply_text("❌ Usuario no encontrado.")
        return

    if db_user.diamonds < cost:
        await update.message.reply_text("💎 No tienes suficientes diamantes.")
        return

    photo = update.message.photo[-1]

    file = await context.bot.get_file(photo.file_id)

    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)

    input_path = f"{TEMP_FOLDER}/{uuid.uuid4()}.jpg"
    output_path = f"{TEMP_FOLDER}/{uuid.uuid4()}_out.jpg"

    await file.download_to_drive(input_path)

    image = Image.open(input_path)

    image = apply_effect(image, effect_name)

    image.save(output_path)

    deduct_diamond(user_id, cost)

    await update.message.reply_photo(photo=open(output_path, "rb"))

    try:
        os.remove(input_path)
        os.remove(output_path)
    except:
        pass
