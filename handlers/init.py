from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters

from handlers.start import start
from handlers.effects import handle_photo
from handlers.router import callback_router


def register_handlers(app):
    """Registra todos los handlers del bot"""

    # =========================
    # COMMANDS
    # =========================
    app.add_handler(CommandHandler("start", start))

    # =========================
    # CALLBACK BUTTONS (ROUTER)
    # =========================
    app.add_handler(CallbackQueryHandler(callback_router))

    # =========================
    # PHOTO HANDLER
    # =========================
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))