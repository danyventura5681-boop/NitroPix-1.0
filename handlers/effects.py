from telegram import Update
from telegram.ext import ContextTypes

from database import add_credits, remove_credits, get_user
from replicate_client import generate_image


# =====================================
# HANDLER PRINCIPAL DE FOTOS
# =====================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe una foto del usuario,
    verifica créditos y genera imagen usando Replicate.
    """

    user_id = update.effective_user.id

    # Obtener usuario
    user = get_user(user_id)

    # Si no existe, crear usuario con créditos iniciales
    if not user:
        add_credits(user_id, 5)
        user = get_user(user_id)

    credits = user["credits"]

    # Verificar créditos
    if credits <= 0:
        await update.message.reply_text(
            "❌ No tienes créditos suficientes."
        )
        return

    await update.message.reply_text("🎨 Generando imagen...")

    try:
        # Obtener la foto en mejor calidad
        photo = update.message.photo[-1]
        file = await photo.get_file()

        # Descargar archivo temporal
        file_path = f"/tmp/{user_id}.jpg"
        await file.download_to_drive(file_path)

        # Generar imagen con Replicate
        result_url = generate_image(file_path)

        # Restar crédito
        remove_credits(user_id, 1)

        # Enviar resultado
        await update.message.reply_photo(
            photo=result_url,
            caption="✅ Imagen generada"
        )

    except Exception as e:
        print("ERROR:", e)

        await update.message.reply_text(
            "⚠️ Ocurrió un error al procesar la imagen."
        )

