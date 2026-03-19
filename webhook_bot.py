import os
import logging

from starlette.applications import Starlette
from starlette.responses import Response, PlainTextResponse, JSONResponse
from starlette.routing import Route

import uvicorn

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# ==============================
# IMPORTAR HANDLERS
# ==============================

from handlers.start import start, button_handler, effect_selector
from handlers.effects import handle_photo


# ==============================
# CONFIG
# ==============================

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN missing")

PORT = int(os.getenv("PORT", 10000))
URL = os.getenv("RENDER_EXTERNAL_URL")

if not URL:
    raise RuntimeError("❌ RENDER_EXTERNAL_URL missing")

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{URL}{WEBHOOK_PATH}"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("nitropix")


# ==============================
# TELEGRAM APPLICATION
# ==============================

telegram_app = Application.builder().token(TOKEN).build()

# COMMAND
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
# WEBHOOK ENDPOINT
# ==============================

async def telegram_webhook(request):
    try:
        data = await request.json()

        update = Update.de_json(data, telegram_app.bot)

        # Enviar update al bot
        await telegram_app.update_queue.put(update)

        return JSONResponse({"status": "ok"})

    except Exception as e:
        logger.exception("❌ Webhook error")
        return JSONResponse({"error": str(e)}, status_code=500)


# ==============================
# HEALTHCHECK (UPTIMEROBOT)
# ==============================

async def health(request):
    return PlainTextResponse("NitroPix alive", status_code=200)


# ==============================
# STARTUP (🔥 CLAVE)
# ==============================

async def startup():

    logger.info("🚀 Starting NitroPix...")

    # Inicializar Telegram
    await telegram_app.initialize()

    # Evitar doble ejecución en Render
    if not telegram_app.running:
        await telegram_app.start()

    # Activar webhook
    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
    )

    logger.info("✅ Webhook activo:")
    logger.info(WEBHOOK_URL)


# ==============================
# SHUTDOWN LIMPIO
# ==============================

async def shutdown():
    logger.info("🛑 Shutting down NitroPix...")

    if telegram_app.running:
        await telegram_app.stop()

    await telegram_app.shutdown()


# ==============================
# STARLETTE APP
# ==============================

app = Starlette(
    routes=[
        Route("/", health, methods=["GET"]),
        Route("/health", health, methods=["GET"]),
        Route("/healthcheck", health, methods=["GET"]),
        Route(WEBHOOK_PATH, telegram_webhook, methods=["POST"]),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown],
)


# ==============================
# RUN LOCAL (NO AFECTA RENDER)
# ==============================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)