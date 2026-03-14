#!/usr/bin/env python3
"""
Script específico para Render
"""
import os
import sys
from bot import main

if __name__ == "__main__":
    # Configurar variables de entorno para Render
    os.environ['PORT'] = os.getenv('PORT', '8080')
    
    # Ejecutar bot
    main()