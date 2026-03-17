import os
import asyncio
import replicate
from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from database import add_credits, remove_credits, get_user

# =========================
# CONFIGURACIÓN REPLICATE
# =========================

replicate_token = os.getenv("REPLICATE_API_TOKEN")

if replicate_token:
    os.environ["REPLICATE_API_TOKEN"] = replicate_token


# =========================
# UTILIDADES
# =========================

async def run_blocking(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


def generate_image(prompt: str):
    """
    Genera imagen usando Replicate
    """
    output = replicate.run(
        "stability-ai/sdxl:39ed52f2a78e9347b4c1a4db3b7d1666d880b303188efd67bdc45015b2b1c6d3",
        input={
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "num_outputs": 1
        }
    )

    if isinstance(output, list):
        return output[0]

    return output


# =========================
# HANDLER PRINCIPAL
# =========================

async def effect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    message = update.message

    if not message:
        return

    # -------------------------
    # validar argumento
    # -------------------------
    if not context.args:
        await message.reply_text(
            "❌ Usa el comando así:\n\n"
            "/effect descripción_de_la_imagen"
        )
        return

    prompt = " ".join(context.args)

    # -------------------------
    # obtener usuario DB
    # -------------------------
    db_user = get_user(user.id)

    if not db_user:
        add_credits(user.id, 5)  # bonus inicial
        db_user = get_user(user.id)

    credits = db_user["credits"]

    cost = Config.EFFECT_COSTS.get("avatar", 1)

    if credits < cost:
        await message.reply_text(
            "❌ No tienes créditos suficientes."
        )
        return

    # -------------------------
    # descontar créditos
    # -------------------------
    remove_credits(user.id, cost)

    status = await message.reply_text("🎨 Generando imagen...")

    try:
        # generar imagen (bloqueante → async)
        image_url = await run_blocking(generate_image, prompt)

        await message.reply_photo(
            photo=image_url,
            caption="✨ Imagen generada con NitroPix"
        )

        await status.delete()

    except Exception as e:
        print("ERROR EFFECT:", e)

        # devolver créditos si falla
        add_credits(user.id, cost)

        await status.edit_text(
            "❌ Error generando la imagen. Intenta nuevamente."
        )


# =========================
# REGISTRO HANDLER
# =========================

def register_effects(application):
    from telegram.ext import CommandHandler

    application.add_handler(
        CommandHandler("effect", effect_command)
    )
