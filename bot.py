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
from database import db
from handlers import start, effects

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Función principal del bot"""
    
    # Crear aplicación
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # ===== HANDLERS =====
    
    # ConversationHandler para el inicio (verificación de grupo)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start.start)],
        states={
            start.WAITING_JOIN: [
                CallbackQueryHandler(start.button_handler, pattern='^(lang_|verify_join)')
            ]
        },
        fallbacks=[]
    )
    application.add_handler(conv_handler)
    
    # Handlers de efectos
    application.add_handler(CallbackQueryHandler(effects.handle_effect, pattern='^effect_'))
    
    # Handlers de navegación
    application.add_handler(CallbackQueryHandler(start.show_languages, pattern='^show_languages$'))
    application.add_handler(CallbackQueryHandler(start.change_language, pattern='^change_lang_'))
    application.add_handler(CallbackQueryHandler(start.button_handler, pattern='^back_to_menu$'))
    
    # Handler para fotos
    application.add_handler(MessageHandler(filters.PHOTO, effects.handle_photo))
    
    # ===== INICIAR BOT =====
    
    # Determinar modo de ejecución (webhook o polling)
    if config.WEBHOOK_URL:
        # Modo webhook (para producción en Render)
        logger.info(f"Iniciando bot en modo webhook en puerto {config.PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            url_path=config.BOT_TOKEN,
            webhook_url=f"{config.WEBHOOK_URL}/{config.BOT_TOKEN}"
        )
    else:
        # Modo polling (para desarrollo local)
        logger.info("Iniciando bot en modo polling")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()