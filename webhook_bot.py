import os
import logging
from starlette.applications import Starlette
from starlette.responses import Response, PlainTextResponse
from starlette.routing import Route
import uvicorn
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Configuración básica
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("No BOT_TOKEN found")

PORT = int(os.environ.get("PORT", 8000))
URL = os.environ.get("RENDER_EXTERNAL_URL", f"https://localhost:{PORT}")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación de Telegram
telegram_app = Application.builder().token(TOKEN).build()

# ===========================================
# HANDLERS BÁSICOS PARA PROBAR
# ===========================================

async def start(update: Update, context):
    await update.message.reply_text("✅ Bot funcionando con webhooks!")

async def echo(update: Update, context):
    await update.message.reply_text(update.message.text)

# Registrar handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ===========================================
# WEBHOOK HANDLER
# ===========================================
async def telegram_webhook(request):
    try:
        request_data = await request.json()
        update = Update.de_json(request_data, telegram_app.bot)
        await telegram_app.update_queue.put(update)
        return Response("ok", status_code=200)
    except Exception as e:
        logger.error(f"Error: {e}")
        return Response("error", status_code=500)

async def health_check(request):
    return PlainTextResponse("OK")

async def setup_webhook():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True
    )
    logger.info(f"✅ Webhook OK: {WEBHOOK_URL}")

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
    uvicorn.run(app, host="0.0.0.0", port=PORT)