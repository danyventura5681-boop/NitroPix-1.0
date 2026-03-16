import os
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import io

# --- Cargar variables del .env ---
load_dotenv()
TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 8080))
URL = os.getenv("URL")
WATERMARK = os.getenv("WATERMARK", "NitroPix Lite Bot")

# --- Función para aplicar efecto simple y marca de agua ---
def apply_watermark(image_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    
    # Crear capa de texto
    txt_layer = Image.new("RGBA", image.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt_layer)

    # Fuente simple, tamaño proporcional
    font_size = max(20, image.size[0] // 20)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = WATERMARK
    textwidth, textheight = draw.textsize(text, font=font)
    position = (image.size[0] - textwidth - 10, image.size[1] - textheight - 10)
    draw.text(position, text, fill=(255,255,255,128), font=font)
    
    # Combinar imagen y marca
    watermarked = Image.alpha_composite(image, txt_layer)
    output = io.BytesIO()
    watermarked.convert("RGB").save(output, format="PNG")
    output.seek(0)
    return output

# --- Comandos del bot ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text("¡Hola! Envía una imagen y te devolveré la versión NitroPix Lite con marca de agua 😉")

def handle_photo(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    image_bytes = photo_file.download_as_bytearray()
    
    result_image = apply_watermark(image_bytes)
    update.message.reply_photo(photo=result_image)

# --- Configuración del bot ---
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# --- Iniciar webhook para Render ---
print(f"Iniciando NitroPix en modo webhook en puerto {PORT}")
updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook(f"{URL}/{TOKEN}")
updater.idle()