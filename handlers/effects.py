import os
from telegram import Update
from telegram.ext import ContextTypes

from database import get_user, deduct_diamond
from utils.effects_engine import apply_effect
from utils.watermark import add_watermark


async def process_effect(update: Update,
                         context: ContextTypes.DEFAULT_TYPE,
                         effect_name: str,
                         cost: int):

    user_id = update.effective_user.id
    db_user = get_user(user_id)

    if not db_user:
        await update.message.reply_text("❌ Usuario no encontrado.")
        return

    if db_user["diamonds"] < cost:
        await update.message.reply_text("💎 Diamantes insuficientes.")
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()

    input_path = f"temp_{user_id}.jpg"
    output_path = f"result_{user_id}.jpg"

    await file.download_to_drive(input_path)

    # aplicar efecto
    img = apply_effect(input_path, effect_name)

    # watermark
    img = add_watermark(img)

    img.save(output_path)

    deduct_diamond(user_id, cost)

    await update.message.reply_photo(
        photo=open(output_path, "rb"),
        caption="✨ Powered by: NitroPix"
    )

    os.remove(input_path)
    os.remove(output_path)
