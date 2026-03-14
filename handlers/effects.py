from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db
from config import config
import os
import aiofiles
import logging
from effects.figura_accion import generar_figura
from effects.avatar import generar_avatar
from effects.dibujo import convertir_dibujo
from effects.artistico import generar_diseno

logger = logging.getLogger(__name__)

# Mapeo de efectos a funciones
EFFECT_FUNCTIONS = {
    'avatar': generar_avatar,
    'figura': generar_figura,
    'dibujo': convertir_dibujo,
    'artistico': generar_diseno
}

# Textos en español (por defecto)
TEXTS = {
    'processing': "⏳ Procesando tu imagen con IA...\nEsto puede tomar unos segundos.",
    'success': "✅ ¡Efecto aplicado con éxito!",
    'insufficient': "❌ Saldo insuficiente. Necesitas {cost} diamantes.",
    'send_photo': "📸 Envíame la foto que quieres transformar:",
    'error': "❌ Error al procesar la imagen. Intenta de nuevo.",
    'powered': "✨ Generado con NitroPix AI",
    'another': "✨ Otro Efecto",
    'menu': "🏠 Menú Principal"
}

async def handle_effect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección de efectos"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    effect = query.data.replace("effect_", "")
    
    # Verificar saldo
    balance = db.get_balance(user_id)
    cost = config.EFFECT_COSTS.get(effect, 2)
    
    if balance < cost:
        keyboard = [[InlineKeyboardButton("💎 Comprar Diamantes", callback_data="buy_diamonds")]]
        await query.edit_message_text(
            TEXTS['insufficient'].format(cost=cost),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Guardar efecto en contexto
    context.user_data['current_effect'] = effect
    context.user_data['effect_cost'] = cost
    
    # Solicitar foto
    effect_names = {
        'avatar': 'Avatar',
        'figura': 'Figura de Acción',
        'dibujo': 'Dibujo',
        'artistico': 'Diseño Artístico'
    }
    
    await query.edit_message_text(
        f"✨ {effect_names[effect]}\n\n{TEXTS['send_photo']}"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la foto recibida"""
    user_id = update.effective_user.id
    
    # Verificar que hay un efecto seleccionado
    if 'current_effect' not in context.user_data:
        await update.message.reply_text("Primero selecciona un efecto del menú.")
        return
    
    effect = context.user_data['current_effect']
    cost = context.user_data['effect_cost']
    
    # Verificar saldo nuevamente
    balance = db.get_balance(user_id)
    if balance < cost:
        await update.message.reply_text(TEXTS['insufficient'].format(cost=cost))
        return
    
    # Mensaje de procesando
    processing_msg = await update.message.reply_text(TEXTS['processing'])
    
    try:
        # Descargar foto
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()
        
        # Crear directorio temporal si no existe
        os.makedirs('temp', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        
        input_path = f"temp/input_{user_id}_{effect}.jpg"
        await photo_file.download_to_drive(input_path)
        
        # Procesar con IA
        effect_function = EFFECT_FUNCTIONS.get(effect)
        if effect_function:
            output_path = await effect_function(input_path, user_id)
            
            if output_path and os.path.exists(output_path):
                # Restar saldo
                new_balance = db.update_balance(user_id, -cost)
                
                # Guardar en BD
                db.save_generated_image(user_id, effect, output_path)
                
                # Enviar resultado
                caption = f"{TEXTS['success']}\n💰 {new_balance} diamantes restantes\n\n{TEXTS['powered']}"
                
                keyboard = [
                    [InlineKeyboardButton(TEXTS['another'], callback_data=f"effect_{effect}")],
                    [InlineKeyboardButton(TEXTS['menu'], callback_data="back_to_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                with open(output_path, 'rb') as img:
                    await update.message.reply_photo(
                        photo=img,
                        caption=caption,
                        reply_markup=reply_markup
                    )
                
                # Limpiar archivos temporales
                os.remove(input_path)
                os.remove(output_path)
            else:
                await update.message.reply_text(TEXTS['error'])
        else:
            await update.message.reply_text("Efecto no implementado aún.")
            
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(TEXTS['error'])
    
    finally:
        await processing_msg.delete()
        # Limpiar contexto si todo salió bien
        if 'current_effect' in context.user_data:
            del context.user_data['current_effect']