import os
import logging

from starlette.applications import Starlette
from starlette.responses import Response, PlainTextResponse
from starlette.routing import Route

import uvicorn

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# IMPORTAR HANDLERS REALES
from handlers.start import start, button_handler, effect_selector
from handlers.effects import handle_photo


# ==============================
# CONFIG
# ==============================

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN missing")

PORT = int(os.environ.get("PORT", 8000))
URL = os.environ.get("RENDER_EXTERNAL_URL")

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==============================
# TELEGRAM APPLICATION
# ==============================

telegram_app = Application.builder().token(TOKEN).build()

# COMMANDS
telegram_app.add_handler(CommandHandler("start", start))

# BUTTONS
telegram_app.add_handler(
    CallbackQueryHandler(effect_selector, pattern="^effect_")
)
telegram_app.add_handler(
    CallbackQueryHandler(button_handler)
)

# PHOTO HANDLER
telegram_app.add_handler(
    MessageHandler(filters.PHOTO, handle_photo)
)


# ==============================
# WEBHOOK
# ==============================

async def telegram_webhook(request):
    try:
        data = await request.json()

        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.update_queue.put(update)

        return Response("ok")

    except Exception as e:
        logger.error(e)
        return Response("error", status_code=500)


# ==============================
# HEALTHCHECK
# ==============================

async def health(request):
    return PlainTextResponse("OK")


# ==============================
# STARTUP (🔥 FIX PRINCIPAL)
# ==============================

async def startup():

    await telegram_app.initialize()
    await telegram_app.start()   # ⭐ ESTA LÍNEA ARREGLA TODO

    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
    )

    logger.info("✅ Webhook activo")
    logger.info(WEBHOOK_URL)


# ==============================
# STARLETTE APP
# ==============================

app = Starlette(
    routes=[
        Route(WEBHOOK_PATH, telegram_webhook, methods=["POST"]),
        Route("/", health),
        Route("/health", health),
        Route("/healthcheck", health),
    ],
    on_startup=[startup],
)


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)