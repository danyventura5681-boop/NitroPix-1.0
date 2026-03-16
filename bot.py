0import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO
import os

# Config logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TOKEN")  # Asegúrate de ponerlo en .env

# Función de start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Bienvenido a NitroPix Lite!\n"
        "Envía una imagen y te aplicaremos un efecto exclusivo con nuestra marca de agua."
    )

# Función para aplicar efecto simple
async def apply_effect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Por favor envía una imagen primero.")
        return

    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = BytesIO()
    await photo_file.download(out=photo_bytes)
    photo_bytes.seek(0)

    # Aplicamos efecto simple: sólo agregamos marca de agua como texto
    # Esto reemplaza Pillow
    effect_image_bytes = BytesIO()
    effect_image_bytes.write(photo_bytes.read())  # De momento, la imagen no se modifica
    effect_image_bytes.seek(0)

    # Enviamos de vuelta con "marca de agua" como caption
    await update.message.reply_photo(
        photo=InputFile(effect_image_bytes, filename="nitropix_lite.jpg"),
        caption="NitroPix Lite 💎"
    )

# Función de ayuda
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envía una foto y nuestro bot aplicará un efecto exclusivo.")

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, apply_effect))

    print("Bot iniciado en modo polling")
    app.run_polling()

if __name__ == "__main__":
    main()