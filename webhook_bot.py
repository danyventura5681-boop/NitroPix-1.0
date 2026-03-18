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
URL = os.environ.get("RENDER_EXTERNAL_URL")

if not URL:
    raise ValueError("❌ RENDER_EXTERNAL_URL no definida")

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
        "✅ NitroPix funcionando correctamente en Render 🚀"
    )


telegram_app.add_handler(CommandHandler("start", start))


# ==============================
# WEBHOOK HANDLER
# ==============================

async def telegram_webhook(request):
    try:
        data = await request.json()

        update = Update.de_json(data, telegram_app.bot)

        # 🔥 enviar update al dispatcher ACTIVO
        await telegram_app.process_update(update)

        return Response("ok", status_code=200)

    except Exception as e:
        logger.exception("❌ Error en webhook")
        return Response("error", status_code=500)


# ==============================
# HEALTH CHECK
# ==============================

async def health_check(request):
    return PlainTextResponse("OK", status_code=200)


# ==============================
# STARTUP / SHUTDOWN
# ==============================

async def startup():
    logger.info("🚀 Inicializando bot...")

    await telegram_app.initialize()
    await telegram_app.start()   # ⭐ ESTA ERA LA PIEZA FALTANTE

    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
    )

    logger.info(f"✅ Webhook configurado: {WEBHOOK_URL}")
    logger.info("✅ Bot listo para recibir mensajes")


async def shutdown():
    logger.info("🛑 Cerrando bot...")
    await telegram_app.stop()
    await telegram_app.shutdown()


# ==============================
# STARLETTE APP
# ==============================

app = Starlette(
    routes=[
        Route(WEBHOOK_PATH, telegram_webhook, methods=["POST"]),
        Route("/health", health_check, methods=["GET"]),
        Route("/healthcheck", health_check, methods=["GET"]),
        Route("/", health_check, methods=["GET"]),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown],
)


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    logger.info(f"🌐 Servidor iniciado en puerto {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)