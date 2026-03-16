import os
import asyncio
import aiohttp
from aiogram import types
from aiogram.types import FSInputFile

# ==============================
# REPLICATE CONFIG
# ==============================

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Solo exigir token cuando corre en Render (producción)
if not REPLICATE_API_TOKEN and os.getenv("RENDER"):
    raise ValueError("REPLICATE_API_TOKEN no configurado")

REPLICATE_MODEL = "stability-ai/sdxl"

HEADERS = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}" if REPLICATE_API_TOKEN else "",
    "Content-Type": "application/json",
}

# Carpeta temporal imágenes
TEMP_DIR = "temp_images"
os.makedirs(TEMP_DIR, exist_ok=True)


# ==============================
# FUNCIONES REPLICATE
# ==============================

async def create_prediction(image_url: str, prompt: str):
    url = "https://api.replicate.com/v1/predictions"

    payload = {
        "version": REPLICATE_MODEL,
        "input": {
            "image": image_url,
            "prompt": prompt,
        },
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=HEADERS) as resp:
            data = await resp.json()
            return data.get("urls", {}).get("get")


async def wait_prediction(get_url: str):
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(get_url, headers=HEADERS) as resp:
                data = await resp.json()

                status = data.get("status")

                if status == "succeeded":
                    return data["output"][0]

                if status == "failed":
                    return None

            await asyncio.sleep(2)


async def download_image(url: str, filepath: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            content = await resp.read()

    with open(filepath, "wb") as f:
        f.write(content)


# ==============================
# PROMPTS DE EFECTOS
# ==============================

EFFECTS = {
    "anime": "anime style, high quality, studio ghibli style, detailed face",
    "realistic": "ultra realistic photo, cinematic lighting, 8k portrait",
    "cyberpunk": "cyberpunk style, neon lights, futuristic city background",
    "cartoon": "pixar cartoon style, colorful, soft lighting",
}


# ==============================
# HANDLER PRINCIPAL
# ==============================

async def handle_photo(message: types.Message):

    if not message.photo:
        return

    await message.reply("🎨 Aplicando efecto NitroPix...")

    # Obtener mejor resolución
    photo = message.photo[-1]

    file = await message.bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"

    # efecto por defecto
    effect = "anime"
    prompt = EFFECTS[effect]

    try:
        # Crear predicción
        get_url = await create_prediction(file_url, prompt)

        if not get_url:
            await message.reply("❌ Error creando efecto.")
            return

        # Esperar resultado
        result_url = await wait_prediction(get_url)

        if not result_url:
            await message.reply("❌ Falló el procesamiento.")
            return

        # Descargar imagen final
        output_path = f"{TEMP_DIR}/{photo.file_id}.png"
        await download_image(result_url, output_path)

        # Enviar imagen
        await message.reply_photo(
            FSInputFile(output_path),
            caption="✨ Efecto aplicado con NitroPix"
        )

    except Exception as e:
        await message.reply(f"⚠️ Error interno:\n{e}")
