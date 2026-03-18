import os
import tempfile

from telegram import Update
from telegram.ext import ContextTypes

from database import add_credits, remove_credits, get_user
from services.ai_effects import cinematic  # efecto inicial


# =====================================
# HANDLER PRINCIPAL DE FOTOS
# =====================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # ===============================
    # USER CHECK
    # ===============================

    user = get_user(user_id)

    if not user:
        add_credits(user_id, 5)
        user = get_user(user_id)

    credits = user["credits"]

    if credits <= 0:
        await update.message.reply_text(
            "❌ No tienes créditos suficientes."
        )
        return

    await update.message.reply_text("🎨 Procesando imagen...")

    tmp_file = None

    try:
        # ===============================
        # DOWNLOAD TELEGRAM IMAGE
        # ===============================

        photo = update.message.photo[-1]
        file = await photo.get_file()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tmp_file = tmp.name

        await file.download_to_drive(tmp_file)

        # ===============================
        # APPLY AI EFFECT
        # ===============================

        # Convertimos path local → URL file compatible
        # ai_effects trabaja con URLs, así que usamos file://
        image_url = f"file://{tmp_file}"

        result_url = cinematic(image_url)

        # ===============================
        # REMOVE CREDIT SOLO SI FUNCIONÓ
        # ===============================

        remove_credits(user_id, 1)

        # ===============================
        # SEND RESULT
        # ===============================

        await update.message.reply_photo(
            photo=result_url,
            caption="✅ Imagen generada"
        )

    except Exception as e:
        print("ERROR effects handler:", e)

        await update.message.reply_text(
            "⚠️ Error procesando la imagen. Intenta nuevamente."
        )

    finally:
        if tmp_file and os.path.exists(tmp_file):
            os.remove(tmp_file)

