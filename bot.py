import os
import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from handlers.effects import handle_photo
from storage.temp_manager import start_cleanup_worker


# ==============================
# LOGGING
# ==============================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ==============================
# VARIABLES DE ENTORNO
# ==============================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN no encontrado en variables de entorno")


# ==============================
# COMANDOS
# ==============================

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Bienvenido a NitroPix Lite\n\n"
        "Envía una foto y aplica efectos IA.\n"
        "Imágenes eliminadas automáticamente en 48h."
    )


async def help_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Cómo usar NitroPix:\n\n"
        "1️⃣ Envía una foto\n"
        "2️⃣ Elige un efecto\n"
        "3️⃣ Recibe tu imagen IA\n\n"
        "Efectos disponibles próximamente 🚀"
    )


# ==============================
# MAIN APP
# ==============================

def main():

    logger.info("Iniciando NitroPix Bot...")

    # Crear aplicación Telegram
    application = Application.builder().token(BOT_TOKEN).build()

    # -------- Handlers --------
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Fotos enviadas por usuarios
    application.add_handler(
        MessageHandler(filters.PHOTO, handle_photo)
    )

    # -------- Cleanup Worker --------
    # elimina imágenes >48h automáticamente
    start_cleanup_worker()

    # -------- Run Bot --------
    logger.info("Bot iniciado correctamente ✅")
    application.run_polling()


# ==============================
# ENTRYPOINT
# ==============================

if __name__ == "__main__":
    main()