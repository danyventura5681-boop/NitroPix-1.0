import os
import logging

from starlette.applications import Starlette
from starlette.responses import Response, PlainTextResponse
from starlette.routing import Route

import uvicorn

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


# ==============================
# CONFIG
# ==============================

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ No BOT_TOKEN found in environment variables")

PORT = int(os.environ.get("PORT", 8000))
URL = os.environ.get("RENDER_EXTERNAL_URL", f"https://localhost:{PORT}")

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{URL}{WEBHOOK_PATH}"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ==============================
# TELEGRAM APPLICATION
# ==============================

telegram_app = Application.builder().token(TOKEN).build()


# ==============================
# COMMANDS
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ NitroPix funcionando con webhooks!"
    )


telegram_app.add_handler(CommandHandler("start", start))


# ==============================
# WEBHOOK HANDLER
# ==============================

async def telegram_webhook(request):
    try:
        data = await request.json()

        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.update_queue.put(update)

        return Response("ok", status_code=200)

    except Exception as e:
        logger.error(f"❌ Error en webhook: {e}")
        return Response("error", status_code=500)


# ==============================
# HEALTH CHECK (RENDER + UPTIMEROBOT)
# ==============================

async def health_check(request):
    return PlainTextResponse("OK")


# ==============================
# SETUP WEBHOOK ON STARTUP
# ==============================

async def setup_webhook():
    await telegram_app.initialize()

    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
    )

    logger.info(f"✅ Webhook configurado en: {WEBHOOK_URL}")
    logger.info("✅ Bot listo para recibir mensajes")


# ==============================
# STARLETTE APP
# ==============================

app = Starlette(
    routes=[
        Route(WEBHOOK_PATH, telegram_webhook, methods=["POST"]),
        Route("/health", health_check, methods=["GET"]),      # ✅ UptimeRobot
        Route("/healthcheck", health_check, methods=["GET"]), # ✅ Compatibilidad
        Route("/", health_check, methods=["GET"]),            # ✅ Root alive
    ],
    on_startup=[setup_webhook],
)


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    logger.info(f"🚀 Iniciando servidor en puerto {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)