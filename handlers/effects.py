import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user, deduct_diamond
from utils.i18n import get_text
import asyncio
import io
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import random
import os

logger = logging.getLogger(__name__)

# ===========================================
# CONFIGURACIÓN DE CRÉDITOS
# ===========================================
CREDIT_TEXT = "⚡ Powered by NitroPix Nova Production ⚡"
SHOW_CREDIT = True  # Cambiar a False si no quieres crédito

# ===========================================
# EFECTOS DISPONIBLES
# ===========================================
EFFECTS = {
    "hd": {
        "name": "✨ Mejorar a HD",
        "description": "Aumenta la resolución y mejora la calidad",
        "cost": 1,
        "emoji": "✨",
        "model": "Real-ESRGAN"
    },
    "manga": {
        "name": "📖 Convertir en Manga",
        "description": "Estilo anime/manga japonés",
        "cost": 2,
        "emoji": "📖",
        "model": "AnimeGANv2"
    },
    "avatar": {
        "name": "🎭 Crear Avatar",
        "description": "Avatar estilizado 3D estilo Pixar",
        "cost": 2,
        "emoji": "🎭",
        "model": "Stable Diffusion"
    },
    "action_figure": {
        "name": "🦸 Figura de Acción",
        "description": "Efecto muñeco / toy figure",
        "cost": 2,
        "emoji": "🦸",
        "model": "ToonYou"
    },
    "drawing": {
        "name": "✏️ Convertir en Dibujo",
        "description": "Estilo sketch / lápiz / carboncillo",
        "cost": 1,
        "emoji": "✏️",
        "model": "CLIP Draw"
    },
    "artistic": {
        "name": "🎨 Diseño Artístico",
        "description": "Filtros artísticos (óleo, acuarela, impresionismo)",
        "cost": 2,
        "emoji": "🎨",
        "model": "VQGAN+CLIP"
    }
}

def add_credit_to_image(image):
    """Añade el texto de crédito a la imagen"""
    if not SHOW_CREDIT:
        return image
    
    # Crear una copia para no modificar la original
    img_with_credit = image.copy()
    
    # Convertir a RGBA si es necesario
    if img_with_credit.mode != 'RGBA':
        img_with_credit = img_with_credit.convert('RGBA')
    
    # Crear una capa para el texto
    txt_layer = Image.new('RGBA', img_with_credit.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    # Intentar cargar una fuente (si no, usar la predeterminada)
    try:
        # Tamaño de fuente proporcional a la imagen
        font_size = max(12, int(img_with_credit.width / 30))
        try:
            font = ImageFont.truetype("/system/fonts/DroidSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Calcular posición (esquina inferior derecha con margen)
    text_width = draw.textlength(CREDIT_TEXT, font=font)
    text_height = font_size
    margin = 15
    position = (
        img_with_credit.width - text_width - margin,
        img_with_credit.height - text_height - margin
    )
    
    # Dibujar sombra primero (para que resalte)
    shadow_position = (position[0] + 2, position[1] + 2)
    draw.text(shadow_position, CREDIT_TEXT, fill=(0, 0, 0, 180), font=font)
    
    # Dibujar texto principal
    draw.text(position, CREDIT_TEXT, fill=(255, 215, 0, 255), font=font)  # Dorado
    
    # Combinar la capa de texto con la imagen
    img_with_credit = Image.alpha_composite(img_with_credit, txt_layer)
    
    # Convertir de vuelta a RGB si era RGB originalmente
    if image.mode == 'RGB':
        img_with_credit = img_with_credit.convert('RGB')
    
    return img_with_credit

async def show_effects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú de efectos"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        return
    
    lang = db_user.language
    text = "🎨 **Elige un efecto mágico:**\n\n"
    text += f"⚡ *Powered by NitroPix Nova Production*\n\n"
    
    keyboard = []
    for effect_id, effect in EFFECTS.items():
        text += f"{effect['emoji']} **{effect['name']}** - {effect['cost']}💎\n"
        keyboard.append([InlineKeyboardButton(
            f"{effect['emoji']} {effect['name']} ({effect['cost']}💎)", 
            callback_data=f"effect_{effect_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("◀️ Volver al Panel", callback_data='panel')])
    
    await query.edit_message_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_effect_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección de un efecto"""
    query = update.callback_query
    await query.answer()
    
    effect_id = query.data.split('_')[1]
    effect = EFFECTS.get(effect_id)
    
    if not effect:
        return
    
    # Guardar el efecto seleccionado
    context.user_data['selected_effect'] = effect_id
    context.user_data['effect_cost'] = effect['cost']
    context.user_data['effect_name'] = effect['name']
    
    user_id = query.from_user.id
    db_user = get_user(user_id)
    
    # Verificar diamantes
    if db_user.diamonds < effect['cost']:
        text = f"❌ Necesitas {effect['cost']}💎 para este efecto.\n\nCompra más diamantes:"
        keyboard = [
            [InlineKeyboardButton("💎 Comprar", callback_data='recharge')],
            [InlineKeyboardButton("◀️ Volver", callback_data='effects')]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Pedir la foto
    text = (
        f"📸 **Envíame la foto para aplicar:**\n\n"
        f"**{effect['name']}**\n"
        f"🤖 Modelo: {effect['model']}\n"
        f"⏳ Tiempo: 15-20 segundos\n"
        f"💎 Costo: {effect['cost']}💎\n\n"
        f"⚡ *Powered by NitroPix Nova Production*"
    )
    keyboard = [[InlineKeyboardButton("◀️ Cancelar", callback_data='effects')]]
    await query.edit_message_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def process_effect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la foto con el efecto seleccionado"""
    user_id = update.effective_user.id
    
    # Verificar si hay un efecto seleccionado
    if 'selected_effect' not in context.user_data:
        await update.message.reply_text("❌ Primero selecciona un efecto desde el menú.")
        return
    
    effect_id = context.user_data['selected_effect']
    effect = EFFECTS.get(effect_id)
    effect_name = context.user_data.get('effect_name', effect['name'])
    cost = context.user_data['effect_cost']
    
    db_user = get_user(user_id)
    
    # Verificar diamantes
    if db_user.diamonds < cost:
        await update.message.reply_text(f"❌ No tienes suficientes diamantes. Necesitas {cost}💎")
        return
    
    # Obtener la foto
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    
    # Descargar la foto
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Mensaje de procesando
    processing_msg = await update.message.reply_text(
        f"🎨 Aplicando **{effect_name}**...\n"
        f"🤖 Modelo: {effect['model']}\n"
        f"⏳ Esto tomará 15-20 segundos\n\n"
        f"⚡ *NitroPix Nova Production*",
        parse_mode='Markdown'
    )
    
    try:
        # ===========================================
        # SIMULACIÓN DE IA (luego conectaremos APIs reales)
        # ===========================================
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Simular tiempo de procesamiento de IA
        await asyncio.sleep(5)
        
        # Aplicar efectos simulados (demo)
        if effect_id == "drawing":
            image = image.filter(ImageFilter.CONTOUR)
            image = image.filter(ImageFilter.SHARPEN)
        elif effect_id == "artistic":
            image = image.filter(ImageFilter.EMBOSS)
            image = image.filter(ImageFilter.SMOOTH_MORE)
        elif effect_id == "hd":
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.3)
        elif effect_id == "manga":
            # Simulación de manga: convertir a escala de grises y aumentar contraste
            image = image.convert('L').convert('RGB')
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
        else:
            # Para avatar, action_figure: efecto de posterización
            image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            image = image.filter(ImageFilter.SMOOTH)
        
        # AÑADIR CRÉDITO A LA IMAGEN
        image_with_credit = add_credit_to_image(image)
        
        # Guardar imagen procesada
        output = io.BytesIO()
        image_with_credit.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        # Descontar diamantes
        deduct_diamond(user_id)
        new_balance = db_user.diamonds - cost
        
        # Eliminar mensaje de procesando
        await processing_msg.delete()
        
        # Enviar foto procesada con crédito
        caption = (
            f"✅ **Efecto aplicado:** {effect_name}\n"
            f"🤖 **Modelo IA:** {effect['model']}\n"
            f"💎 **Diamantes restantes:** {new_balance}\n\n"
            f"⚡ *Powered by NitroPix Nova Production* ⚡"
        )
        
        await update.message.reply_photo(
            photo=output,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎨 Otro Efecto", callback_data='effects'),
                InlineKeyboardButton("🏠 Panel Principal", callback_data='panel')
            ]])
        )
        
        # Limpiar contexto
        del context.user_data['selected_effect']
        del context.user_data['effect_cost']
        del context.user_data['effect_name']
        
    except Exception as e:
        logger.error(f"Error processing effect: {e}")
        await processing_msg.delete()
        await update.message.reply_text(
            "❌ Error al procesar la imagen. Intenta de nuevo.\n\n"
            "⚡ *NitroPix Nova Production*",
            parse_mode='Markdown'
        )