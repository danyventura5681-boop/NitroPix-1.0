import os
import logging
import replicate
from typing import Optional, List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener token directamente de variables de entorno
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

# Verificar si el token existe (solo warning en tests)
if not REPLICATE_API_TOKEN:
    logger.warning("REPLICATE_API_TOKEN no está configurado. Modo simulación activado.")
else:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

def generate_image(prompt: str) -> Optional[str]:
    """
    Genera una imagen usando Replicate.
    Retorna la URL de la imagen o None si falla.
    """
    # Si no hay token, modo simulación (para tests)
    if not REPLICATE_API_TOKEN:
        logger.info("Modo simulación: retornando URL falsa")
        return "https://example.com/simulated_image.jpg"
    
    try:
        output = replicate.run(
            "stability-ai/sdxl",
            input={"prompt": prompt}
        )
        
        # Replicate retorna una lista de URLs
        if output and isinstance(output, list) and len(output) > 0:
            logger.info(f"Imagen generada exitosamente: {output[0]}")
            return output[0]
        else:
            logger.error("Respuesta inesperada de Replicate")
            return None
            
    except Exception as e:
        logger.error(f"Error al generar imagen con Replicate: {e}")
        return None

# Función de compatibilidad para uso más específico con efectos
def generate_image_with_effect(image_bytes: bytes, effect: str) -> Optional[str]:
    """
    Versión especializada para usar con efectos predefinidos.
    Por implementar - actualmente usa SDXL.
    """
    prompt = f"Apply {effect} effect to the provided image"
    return generate_image(prompt)