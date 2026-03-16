from telegram import Update
from telegram.ext import ContextTypes

from services.ai_effects import (
    upscale_hd,
    anime_style,
    manga_style,
    action_figure,
    cinematic
)

from utils.downloader import get_telegram_file_url


async def process_effect(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.photo:
        await update.message.reply_text("Envía una imagen primero.")
        return

    await update.message.reply_text("Procesando imagen IA... 🚀")

    photo = update.message.photo[-1]
    image_url = await get_telegram_file_url(
        context.bot,
        photo.file_id
    )

    effect = context.user_data.get("effect")

    if effect == "hd":
        result = upscale_hd(image_url)

    elif effect == "anime":
        result = anime_style(image_url)

    elif effect == "manga":
        result = manga_style(image_url)

    elif effect == "figure":
        result = action_figure(image_url)

    elif effect == "cinematic":
        result = cinematic(image_url)

    else:
        await update.message.reply_text("Efecto no válido.")
        return

    await update.message.reply_photo(result)
