import os
import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Handlers
from handlers.start import start, button_handler, effect_selector
from handlers.effects import handle_photo

from storage.temp_manager import start_cleanup_worker

# 🔥 KEEP ALIVE (IMPORTANTE PARA RENDER WEB SERVICE)
from keep_alive import keep_alive


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

# Permitir tests en GitHub Actions
if not BOT_TOKEN and not os.getenv("GITHUB_ACTIONS"):
    raise ValueError("BOT_TOKEN no encontrado en variables de entorno")


# ==============================
# HELP COMMAND
# ==============================

async def help_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Cómo usar NitroPix:\n\n"
        "1️⃣ Usa /start\n"
        "2️⃣ Selecciona un efecto\n"
        "3️⃣ Envía una foto\n"
        "4️⃣ Recibe tu imagen IA 🚀"
    )


# ==============================
# MAIN APP
# ==============================

def main():

    logger.info("Iniciando NitroPix Bot...")

    # 🔥 Inicia servidor web para Render (PUERTO 8080)
    keep_alive()

    # Crear aplicación Telegram
    application = Application.builder().token(BOT_TOKEN).build()

    # ---------------- COMMANDS ----------------
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # ---------------- BUTTONS ----------------
    # Selector de efectos (más específico primero)
    application.add_handler(
        CallbackQueryHandler(effect_selector, pattern="^effect_")
    )

    # Otros botones
    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # ---------------- PHOTO HANDLER ----------------
    application.add_handler(
        MessageHandler(filters.PHOTO, handle_photo)
    )

    # ---------------- CLEANUP WORKER ----------------
    start_cleanup_worker()

    # ---------------- RUN BOT ----------------
    logger.info("Bot iniciado correctamente ✅")
    application.run_polling()


# ==============================
# ENTRYPOINT
# ==============================

if __name__ == "__main__":
    main()