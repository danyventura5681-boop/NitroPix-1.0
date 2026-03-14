import os
import logging
from starlette.applications import Starlette
from starlette.responses import Response, PlainTextResponse
from starlette.routing import Route
import uvicorn
from telegram import Update
from telegram.ext import Application, CommandHandler

# Configuración básica
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ No BOT_TOKEN found in environment variables")

PORT = int(os.environ.get("PORT", 8000))
URL = os.environ.get("RENDER_EXTERNAL_URL", f"https://localhost:{PORT}")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación de Telegram
telegram_app = Application.builder().token(TOKEN).build()

# Handler simple
async def start(update: Update, context):
    await update.message.reply_text("✅ NitroPix funcionando con webhooks!")

telegram_app.add_handler(CommandHandler("start", start))

# Webhook handler
async def telegram_webhook(request):
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.update_queue.put(update)
        return Response("ok", status_code=200)
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return Response("error", status_code=500)

# Health check para Render
async def health_check(request):
    return PlainTextResponse("OK")

# Configurar webhook al inicio
async def setup_webhook():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True
    )
    logger.info(f"✅ Webhook configurado en: {WEBHOOK_URL}")
    logger.info("✅ Bot listo para recibir mensajes")

# App Starlette
app = Starlette(
    routes=[
        Route(WEBHOOK_PATH, telegram_webhook, methods=["POST"]),
        Route("/healthcheck", health_check, methods=["GET"]),
        Route("/", health_check, methods=["GET"]),
    ],
    on_startup=[setup_webhook]
)

if __name__ == "__main__":
    logger.info(f"🚀 Iniciando servidor en puerto {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)