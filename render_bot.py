#!/usr/bin/env python3
"""
Punto de entrada para Render en producción.
"""
import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Configurar puerto desde variable de entorno
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Iniciando NitroPix en modo webhook en puerto {port}")
        
        # Importar la función principal del bot
        from bot import main
        main()
    except Exception as e:
        logger.exception("Error fatal al iniciar el bot")
        sys.exit(1)