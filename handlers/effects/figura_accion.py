import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os
import random
import logging

logger = logging.getLogger(__name__)

# Configuración del modelo
MODEL_ID = "dreamshaper/dreamshaper_8"  # Modelo gratuito optimizado para figuras
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

# Prompts especializados
BASE_PROMPT = """
highly detailed 1/7 scale commercial action figure, realistic PVC figure,
professional product photography, studio lighting, 8k resolution,
collector's edition, dynamic pose, on round transparent acrylic base,
bandai-style packaging, {subject_description}, ultra detailed, sharp focus
"""

NEGATIVE_PROMPT = """
blurry, low quality, distorted, ugly, bad anatomy, watermark, text, logo,
cartoon, 2d, painting, drawing, anime, manga, illustration, worst quality,
low resolution, jpeg artifacts, signature, username, artist name
"""

# Cache del pipeline
_pipeline = None

def get_pipeline():
    """Carga o retorna el pipeline cacheado"""
    global _pipeline
    if _pipeline is None:
        logger.info("Cargando modelo de figuras de acción...")
        try:
            _pipeline = StableDiffusionPipeline.from_pretrained(
                MODEL_ID,
                torch_dtype=DTYPE,
                safety_checker=None,
                requires_safety_checker=False,
                use_safetensors=True
            )
            _pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                _pipeline.scheduler.config
            )
            _pipeline = _pipeline.to(DEVICE)
            
            # Optimizaciones
            if DEVICE == "cuda":
                _pipeline.enable_attention_slicing()
                _pipeline.enable_xformers_memory_efficient_attention()
            
            logger.info("Modelo cargado exitosamente en {}".format(DEVICE))
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise
    return _pipeline

async def generar_figura(input_image_path, user_id):
    """
    Genera una figura de acción a partir de una imagen
    """
    try:
        # Analizar la imagen de entrada para obtener descripción
        # Por ahora usamos un prompt genérico basado en el efecto
        subject_description = "cool character with detailed clothing and accessories"
        
        # Construir prompt completo
        prompt = BASE_PROMPT.format(subject_description=subject_description)
        
        # Obtener pipeline
        pipe = get_pipeline()
        
        # Configuración de generación
        generator = torch.Generator(device=DEVICE).manual_seed(random.randint(1, 999999))
        
        # Generar imagen
        with torch.no_grad():
            result = pipe(
                prompt=prompt,
                negative_prompt=NEGATIVE_PROMPT,
                num_inference_steps=30,
                guidance_scale=7.5,
                width=768,
                height=768,
                generator=generator
            ).images[0]
        
        # Guardar resultado
        output_filename = f"output/figura_{user_id}_{random.randint(1000,9999)}.jpg"
        result.save(output_filename, quality=95)
        
        return output_filename
        
    except Exception as e:
        logger.error(f"Error en generar_figura: {e}")
        return None