import os
import asyncio
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ContextTypes

from database import get_user, deduct_diamond


async def process_effect(update: Update, context: ContextTypes.DEFAULT_TYPE, effect_name: str, cost: int):

    user = update.effective_user
    user_id = user.id

    db_user = get_user(user_id)

    if not db_user:
        await update.message.reply_text("❌ Usuario no encontrado.")
        return

    if db_user.diamonds < cost:
        await update.message.reply_text(
            f"❌ No tienes suficientes diamantes.\n\n💎 Necesitas: {cost}\n💎 Tienes: {db_user.diamonds}"
        )
        return

    if not update.message.photo:
        await update.message.reply_text("📸 Envía una imagen primero.")
        return

    # Descargar imagen
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    os.makedirs("temp", exist_ok=True)

    input_path = f"temp/{photo.file_id}.jpg"
    output_path = f"temp/{photo.file_id}_edited.jpg"

    await file.download_to_drive(input_path)

    await update.message.reply_text("⚡ Procesando imagen...")

    try:

        image = Image.open(input_path)

        # --------------------
        # EFECTOS DISPONIBLES
        # --------------------

        if effect_name == "blur":
            image = image.filter(ImageFilter.GaussianBlur(8))

        elif effect_name == "sharpen":
            image = image.filter(ImageFilter.SHARPEN)

        elif effect_name == "bright":
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.6)

        elif effect_name == "contrast":
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.7)

        elif effect_name == "bw":
            image = image.convert("L")

        elif effect_name == "anime":
            image = image.filter(ImageFilter.EDGE_ENHANCE)

        # --------------------
        # Marca NitroPix
        # --------------------

        img_with_credit = image.copy()
        draw = ImageDraw.Draw(img_with_credit)

        font_size = max(12, int(img_with_credit.width / 30))
        font = ImageFont.load_default()

        text = "NitroPix"

        text_position = (
            img_with_credit.width - (len(text) * font_size),
            img_with_credit.height - font_size - 10
        )

        draw.text(text_position, text, fill=(255, 255, 255), font=font)

        img_with_credit.save(output_path)

        # --------------------
        # Descontar diamantes
        # --------------------

        deduct_diamond(user_id, cost)

        updated_user = get_user(user_id)

        # --------------------
        # Enviar imagen
        # --------------------

        with open(output_path, "rb") as img:
            await update.message.reply_photo(
                img,
                caption=f"✨ Efecto aplicado!\n\n💎 Diamantes restantes: {updated_user.diamonds}"
            )

    except Exception as e:

        await update.message.reply_text("❌ Error procesando la imagen.")

        print("ERROR EFFECT:", e)

    finally:

        try:
            image.close()
        except:
            pass

        try:
            os.remove(input_path)
        except:
            pass

        try:
            os.remove(output_path)
        except:
            pass