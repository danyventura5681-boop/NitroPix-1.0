import os
import io
import asyncio
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_user, deduct_diamond

# ----- CONFIGURACIÓN -----
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
SHOW_CREDIT = True
CREDIT_TEXT = "Telegram Bot - Powered by NitroPix"

# ----- EFECTOS DISPONIBLES -----
EFFECTS = {
    "hd": {
        "name": "✨ Mejorar HD",
        "cost": 1,
        "description": "Mejora nitidez y contraste"
    },
    "sketch": {
        "name": "✏️ Dibujo / Sketch",
        "cost": 1,
        "description": "Convierte la foto en dibujo a lápiz"
    },
    "comic": {
        "name": "📖 Comic / Manga",
        "cost": 2,
        "description": "Estilo cómic japonés"
    },
    "avatar": {
        "name": "🎭 Avatar Cartoon",
        "cost": 2,
        "description": "Avatar estilo caricatura 3D simple"
    },
    "vintage": {
        "name": "🕰️ Vintage / Retro",
        "cost": 2,
        "description": "Filtros estilo retro o sepia"
    },
    "artistic": {
        "name": "🎨 Filtro Artístico",
        "cost": 3,
        "description": "Estilo óleo, acuarela o pintura"
    }
}

# ----- FUNCIONES AUXILIARES -----
def add_watermark(image: Image.Image) -> Image.Image:
    """Agrega la marca de agua NitroPix + logo"""
    img = image.convert("RGBA")

    # Cargar logo
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((int(img.width * 0.15), int(img.height * 0.15)))
        img.paste(logo, (img.width - logo.width - 10, img.height - logo.height - 10), logo)
    except Exception:
        pass  # si no hay logo, ignorar

    # Texto
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    font_size = max(12, int(img.width / 25))
    try:
        font = ImageFont.truetype("/system/fonts/DroidSans.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    text_width, text_height = draw.textsize(CREDIT_TEXT, font=font)
    position = (10, img.height - text_height - 10)
    draw.text(position, CREDIT_TEXT, fill=(255, 255, 255, 200), font=font)

    combined = Image.alpha_composite(img, txt_layer)
    return combined.convert("RGB")

def apply_effect(image: Image.Image, effect_id: str) -> Image.Image:
    """Aplica efecto seleccionado a la imagen"""
    if effect_id == "hd":
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)
    elif effect_id == "sketch":
        image = image.convert("L").filter(ImageFilter.CONTOUR).filter(ImageFilter.SHARPEN).convert("RGB")
    elif effect_id == "comic":
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.SMOOTH)
    elif effect_id == "avatar":
        image = image.filter(ImageFilter.SMOOTH).filter(ImageFilter.SHARPEN)
    elif effect_id == "vintage":
        image = image.convert("L").convert("RGB")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
    elif effect_id == "artistic":
        image = image.filter(ImageFilter.EMBOSS).filter(ImageFilter.SMOOTH_MORE)
    return image

# ----- MENÚ DE EFECTOS -----
async def show_effects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        return

    balance = db_user.diamonds
    text = f"🎨 **Elige un efecto mágico:**\n\n💎 Tus diamantes: {balance}\n⚡ Powered by NitroPix\n\n"
    keyboard = []

    for effect_id, effect in EFFECTS.items():
        text += f"{effect['name']} - {effect['cost']}💎\n"
        keyboard.append([InlineKeyboardButton(f"{effect['name']} ({effect['cost']}💎)", callback_data=f"effect_{effect_id}")])

    keyboard.append([InlineKeyboardButton("🏠 Panel Principal", callback_data="panel")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ----- PROCESAR FOTO -----
async def process_effect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = get_user(user_id)

    if 'selected_effect' not in context.user_data:
        await update.message.reply_text("❌ Primero selecciona un efecto desde el menú.")
        return

    effect_id = context.user_data['selected_effect']
    cost = context.user_data['effect_cost']
    effect_name = context.user_data['effect_name']

    if db_user.diamonds < cost:
        await update.message.reply_text(f"❌ No tienes suficientes diamantes. Necesitas {cost}💎")
        return

    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    msg = await update.message.reply_text(f"🎨 Aplicando **{effect_name}**... ⚡ Powered by NitroPix", parse_mode="Markdown")

    try:
        image = Image.open(io.BytesIO(photo_bytes))
        await asyncio.sleep(1)  # simulación de tiempo de procesamiento
        image = apply_effect(image, effect_id)
        image = add_watermark(image)

        output = io.BytesIO()
        image.save(output, format="JPEG", quality=90)
        output.seek(0)

        # Deduce diamantes
        deduct_diamond(user_id)

        await msg.delete()
        await update.message.reply_photo(
            photo=output,
            caption=f"✅ **Efecto aplicado:** {effect_name}\n💎 Diamantes restantes: {db_user.diamonds - cost}\n⚡ Powered by NitroPix",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎨 Otro Efecto", callback_data="effects"),
                InlineKeyboardButton("🏠 Panel Principal", callback_data="panel")
            ]]),
            parse_mode="Markdown"
        )

        # Limpiar context
        del context.user_data['selected_effect']
        del context.user_data['effect_cost']
        del context.user_data['effect_name']

    except Exception as e:
        await msg.delete()
        await update.message.reply_text(f"❌ Error al procesar la imagen. Intenta de nuevo.\n\n{e}")
