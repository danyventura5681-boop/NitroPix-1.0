#!/usr/bin/env python3
"""
NitroPix Bot - Transforma tus fotos con IA
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

from config import config
from handlers import start, effects


# ==============================
# CONFIGURAR LOGGING
# ==============================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# ==============================
# FUNCIÓN PRINCIPAL
# ==============================

def main():

    logger.info("🚀 Iniciando NitroPix...")

    # Crear aplicación
    application = (
        Application.builder()
        .token(config.BOT_TOKEN)
        .build()
    )

    # ==============================
    # HANDLERS
    # ==============================

    # Conversación inicial (verificación grupo)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start.start)],
        states={
            start.WAITING_JOIN: [
                CallbackQueryHandler(
                    start.button_handler,
                    pattern="^(lang_|verify_join)"
                )
            ]
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)

    # ==============================
    # EFECTOS
    # ==============================

    application.add_handler(
        CallbackQueryHandler(
            effects.handle_effect,
            pattern="^effect_"
        )
    )

    # ==============================
    # NAVEGACIÓN
    # ==============================

    application.add_handler(
        CallbackQueryHandler(
            start.show_languages,
            pattern="^show_languages$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            start.change_language,
            pattern="^change_lang_"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            start.button_handler,
            pattern="^back_to_menu$"
        )
    )

    # ==============================
    # FOTOS
    # ==============================

    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            effects.handle_photo
        )
    )

    # ==============================
    # INICIAR BOT
    # ==============================

    try:

        # Modo webhook (Render producción)
        if config.WEBHOOK_URL:

            logger.info("🌐 Ejecutando en modo WEBHOOK")

            application.run_webhook(
                listen="0.0.0.0",
                port=int(config.PORT),
                url_path=config.BOT_TOKEN,
                webhook_url=f"{config.WEBHOOK_URL}/{config.BOT_TOKEN}",
                drop_pending_updates=True
            )

        # Modo polling (desarrollo)
        else:

            logger.info("💻 Ejecutando en modo POLLING")

            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )

    except Exception as e:

        logger.error(f"❌ Error iniciando el bot: {e}")


# ==============================
# ENTRY POINT
# ==============================

if __name__ == "__main__":
    main()