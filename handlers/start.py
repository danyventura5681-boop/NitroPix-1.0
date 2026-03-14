from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from config import config
import logging

logger = logging.getLogger(__name__)

# Estados
WAITING_JOIN = 1

# Textos multilenguaje
TEXTS = {
    'es': {
        'welcome': "🎨 ¡Bienvenido a NitroPix, {name}!\n\nPara usar el bot, primero debes unirte a nuestro grupo oficial:",
        'welcome_back': "🎨 ¡Bienvenido de nuevo, {name}!",
        'join_group': "🔗 Unirse al Grupo",
        'verify': "✅ Verificar y Continuar",
        'not_joined': "❌ Aún no te has unido. Por favor, únete al grupo y haz clic en 'Verificar'",
        'verified': "✅ ¡Verificado! Bienvenido a NitroPix",
        'main_menu': "📱 Panel Principal",
        'balance': "💰 Saldo: {balance} diamantes",
        'select_effect': "✨ Selecciona un efecto mágico:",
        'language': "🌐 Idioma",
        'buy': "💎 Comprar Diamantes",
        'effects': {
            'avatar': "✨ Crear Avatar",
            'figura': "🎭 Figura de Acción",
            'dibujo': "✏️ Convertir en Dibujo",
            'artistico': "🎨 Diseño Artístico"
        }
    },
    'en': {
        'welcome': "🎨 Welcome to NitroPix, {name}!\n\nTo use the bot, you must first join our official group:",
        'welcome_back': "🎨 Welcome back, {name}!",
        'join_group': "🔗 Join Group",
        'verify': "✅ Verify and Continue",
        'not_joined': "❌ You haven't joined yet. Please join the group and click 'Verify'",
        'verified': "✅ Verified! Welcome to NitroPix",
        'main_menu': "📱 Main Panel",
        'balance': "💰 Balance: {balance} diamonds",
        'select_effect': "✨ Select a magic effect:",
        'language': "🌐 Language",
        'buy': "💎 Buy Diamonds",
        'effects': {
            'avatar': "✨ Create Avatar",
            'figura': "🎭 Action Figure",
            'dibujo': "✏️ Convert to Drawing",
            'artistico': "🎨 Artistic Design"
        }
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Crear o actualizar usuario
    db.create_user(user_id, user.username, user.first_name)
    db.update_last_active(user_id)
    
    # Verificar si ya se unió al grupo
    if db.has_joined_group(user_id):
        await show_main_menu(update, context)
        return ConversationHandler.END
    
    # Mostrar mensaje de bienvenida con selector de idioma
    keyboard = [
        [
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
        ],
        [InlineKeyboardButton(TEXTS['es']['join_group'], url=config.GROUP_LINK)],
        [InlineKeyboardButton(TEXTS['es']['verify'], callback_data="verify_join")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        TEXTS['es']['welcome'].format(name=user.first_name),
        reply_markup=reply_markup
    )
    
    return WAITING_JOIN

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Cambiar idioma
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        db.set_language(user_id, lang)
        
        # Actualizar mensaje con nuevo idioma
        keyboard = [
            [
                InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
                InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
            ],
            [InlineKeyboardButton(TEXTS[lang]['join_group'], url=config.GROUP_LINK)],
            [InlineKeyboardButton(TEXTS[lang]['verify'], callback_data="verify_join")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            TEXTS[lang]['welcome'].format(name=query.from_user.first_name),
            reply_markup=reply_markup
        )
        return WAITING_JOIN
    
    # Verificar unión al grupo
    elif data == "verify_join":
        # Aquí podrías verificar realmente con Telegram API
        # Por ahora, asumimos que sí se unió
        db.set_joined_group(user_id)
        
        lang = db.get_language(user_id)
        await query.edit_message_text(
            TEXTS[lang]['verified']
        )
        await show_main_menu_callback(query, context)
        return ConversationHandler.END
    
    # Volver al menú principal
    elif data == "back_to_menu":
        await show_main_menu_callback(query, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el menú principal (desde mensaje)"""
    user_id = update.effective_user.id
    balance = db.get_balance(user_id)
    lang = db.get_language(user_id)
    
    keyboard = get_main_menu_keyboard(lang)
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{TEXTS[lang]['balance'].format(balance=balance)}\n\n{TEXTS[lang]['select_effect']}",
        reply_markup=reply_markup
    )

async def show_main_menu_callback(query, context):
    """Muestra el menú principal (desde callback)"""
    user_id = query.from_user.id
    balance = db.get_balance(user_id)
    lang = db.get_language(user_id)
    
    keyboard = get_main_menu_keyboard(lang)
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{TEXTS[lang]['balance'].format(balance=balance)}\n\n{TEXTS[lang]['select_effect']}",
        reply_markup=reply_markup
    )

def get_main_menu_keyboard(lang):
    """Genera el teclado del menú principal"""
    return [
        [InlineKeyboardButton(TEXTS[lang]['effects']['avatar'], callback_data="effect_avatar")],
        [InlineKeyboardButton(TEXTS[lang]['effects']['figura'], callback_data="effect_figura")],
        [InlineKeyboardButton(TEXTS[lang]['effects']['dibujo'], callback_data="effect_dibujo")],
        [InlineKeyboardButton(TEXTS[lang]['effects']['artistico'], callback_data="effect_artistico")],
        [
            InlineKeyboardButton(TEXTS[lang]['buy'], callback_data="buy_diamonds"),
            InlineKeyboardButton(TEXTS[lang]['language'], callback_data="show_languages")
        ]
    ]

async def show_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el selector de idiomas"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    balance = db.get_balance(user_id)
    current_lang = db.get_language(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton("🇪🇸 Español", callback_data="change_lang_es"),
            InlineKeyboardButton("🇺🇸 English", callback_data="change_lang_en")
        ],
        [InlineKeyboardButton("🔙 Volver / Back", callback_data="back_to_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    lang_text = "Selecciona tu idioma:" if current_lang == 'es' else "Select your language:"
    
    await query.edit_message_text(
        f"💰 {balance} diamantes\n\n🌐 {lang_text}",
        reply_markup=reply_markup
    )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cambia el idioma del usuario"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = query.data.split("_")[2]
    
    db.set_language(user_id, lang)
    await show_main_menu_callback(query, context)