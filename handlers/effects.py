import os
import tempfile
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from database import add_credits, remove_credits, get_user
from services.ai_effects import cinematic


# =====================================
# USERS EN PROCESO (ANTI SPAM / DUPLICADO)
# =====================================

processing_users = set()


# =====================================
# HANDLER PRINCIPAL DE FOTOS
# =====================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # -------------------------------
    # EVITAR DOBLE PROCESAMIENTO
    # -------------------------------

    if user_id in processing_users:
        await update.message.reply_text(
            "⏳ Ya estoy procesando una imagen tuya..."
        )
        return

    processing_users.add(user_id)

    tmp_file = None

    try:
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

        # ===============================
        # DOWNLOAD TELEGRAM IMAGE
        # ===============================

        photo = update.message.photo[-1]
        file = await photo.get_file()

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tmp_file = tmp.name

        await file.download_to_drive(tmp_file)

        # ===============================
        # APPLY AI EFFECT (NO BLOQUEANTE)
        # ===============================

        image_url = f"file://{tmp_file}"

        # Ejecutar IA fuera del event loop
        result_url = await asyncio.to_thread(
            cinematic,
            image_url
        )

        # ===============================
        # REMOVE CREDIT SOLO SI FUNCIONÓ
        # ===============================

        remove_credits(user_id, 1)

        # ===============================
        # SEND RESULT
        # ===============================

        await update.message.reply_photo(
            photo=result_url,
            caption="✅ Imagen generada (-1 crédito)"
        )

    except Exception as e:
        print("ERROR effects handler:", e)

        await update.message.reply_text(
            "⚠️ Error procesando la imagen. Intenta nuevamente."
        )

    finally:
        # limpiar archivo temporal
        if tmp_file and os.path.exists(tmp_file):
            os.remove(tmp_file)

        # liberar usuario
        processing_users.discard(user_id)

