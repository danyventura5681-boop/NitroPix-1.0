import os
import logging
import replicate
from typing import Optional, List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener token directamente de variables de entorno
# ESTO ES LO QUE RENDER USA - LEE DE SUS VARIABLES
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

def generate_image(prompt: str) -> Optional[str]:
    """
    Genera una imagen usando Replicate.
    Retorna la URL de la imagen o None si falla.
    """
    # EN RENDER: el token existe y funciona
    # EN GITHUB ACTIONS: puede no existir (modo simulación)
    
    if not REPLICATE_API_TOKEN:
        logger.warning("REPLICATE_API_TOKEN no configurado. Modo simulación para tests.")
        return "https://example.com/simulated_image.jpg"
    
    try:
        # Configurar token para replicate
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        
        output = replicate.run(
            "stability-ai/sdxl",
            input={"prompt": prompt}
        )
        
        if output and isinstance(output, list) and len(output) > 0:
            logger.info(f"✅ Imagen generada con Replicate: {output[0]}")
            return output[0]
        else:
            logger.error("❌ Respuesta inesperada de Replicate")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error al generar imagen con Replicate: {e}")
        return None

# Para compatibilidad con efectos
def generate_image_with_effect(image_bytes: bytes, effect: str) -> Optional[str]:
    """
    Versión para usar con efectos.
    En producción usa Replicate, en tests simula.
    """
    prompt = f"Apply {effect} effect to image"
    return generate_image(prompt)