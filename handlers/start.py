from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user, create_user, update_user_language, get_user_by_referral_code, is_banned, has_joined_group, set_user_joined_group
from utils.i18n import get_text
from config import GROUP_LINK

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    
    if is_banned(telegram_id):
        await update.message.reply_text(get_text('user_banned', 'en'))
        return
    
    args = context.args

    referred_by = None
    if args and args[0].startswith('ref_'):
        ref_code = args[0][4:]
        referrer = get_user_by_referral_code(ref_code)
        if referrer:
            referred_by = referrer.telegram_id

    db_user = get_user(telegram_id)
    if not db_user:
        db_user = create_user(telegram_id, user.username, user.first_name, referred_by)
        await update.message.reply_text(
            get_text('welcome', 'en') + "\n\n" + get_text('choose_language', 'en'),
            reply_markup=language_keyboard()
        )
    else:
        await update.message.reply_text(
            get_text('choose_language', db_user.language),
            reply_markup=language_keyboard()
        )

def language_keyboard():
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("Español 🇪🇸", callback_data="lang_es")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    telegram_id = query.from_user.id

    update_user_language(telegram_id, lang)
    await query.edit_message_text(get_text('language_selected', lang))
    
    # Después de elegir idioma, preguntar si quiere unirse al grupo
    await ask_join_group(update, context)

async def ask_join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pregunta al usuario si quiere unirse al grupo oficial"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Si ya se unió antes, ir directo al panel
    if has_joined_group(user_id):
        await panel_menu(update, context)
        return
    
    # Texto de invitación
    text = (
        "💎 **¡Únete a nuestra comunidad!** 💎\n\n"
        "Antes de continuar, ¿te gustaría unirte al grupo oficial de NitroPix?\n"
        "✅ Obtén soporte\n"
        "✅ Conoce las últimas novedades\n"
        "✅ Participa en eventos exclusivos\n\n"
        "👉 Haz clic en el botón de abajo para unirte, luego presiona **'Verifiqué'**.\n\n"
        "🎁 **Recompensa: +0.5💎 por unirte**"
    )
    
    keyboard = [
        [InlineKeyboardButton("📢 Unirme al Grupo", url=GROUP_LINK)],
        [InlineKeyboardButton("✅ Ya me uní / Verifiqué", callback_data='verify_group')],
        [InlineKeyboardButton("⏭️ Omitir", callback_data='skip_group')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def verify_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica que el usuario dice que se unió"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Marcar en base de datos
    set_user_joined_group(user_id)
    
    # Dar una pequeña recompensa por unirse
    from database import add_diamonds
    new_balance = add_diamonds(user_id, 0.5)
    
    await query.edit_message_text(
        f"✅ **¡Gracias por unirte!**\n\nHas recibido **+0.5💎** como bienvenida.\n\n💰 Nuevo saldo: {new_balance}💎\n\nCargando tu panel...",
        parse_mode='Markdown'
    )
    await panel_menu(update, context)

async def skip_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usuario omite unirse al grupo"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏭️ Omitido. Puedes unirte más tarde desde el menú.")
    await panel_menu(update, context)

async def panel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
    else:
        user_id = update.effective_user.id
        query = None

    if is_banned(user_id):
        if query:
            await query.edit_message_text(get_text('user_banned', 'en'))
        else:
            await update.message.reply_text(get_text('user_banned', 'en'))
        return

    db_user = get_user(user_id)
    if not db_user:
        return

    lang = db_user.language
    username = db_user.first_name or db_user.username or "User"
    
    # TEXTO DEL PANEL ORIGINAL
    text = get_text('panel_title', lang, 
                   username=username,
                   user_id=user_id,
                   balance=db_user.diamonds)

    # BOTONES CON 💎
    keyboard = [
        [InlineKeyboardButton("💎 Comprar Diamantes", callback_data='recharge')],
        [InlineKeyboardButton("🚀 Invitar Amigos 💎", callback_data='referral')],
        [InlineKeyboardButton("🎁 Regalo Diario 💎", callback_data='daily')],
        [InlineKeyboardButton("⚡️ Procesa mi Foto 💎", callback_data='effects')]  # <-- Lleva a efectos
    ]
    
    # Si es admin, añadir botón de admin panel
    if db_user.is_admin:
        keyboard.append([InlineKeyboardButton("🛡️ Admin Panel", callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')