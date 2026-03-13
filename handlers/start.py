from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user, create_user, update_user_language, get_user_by_referral_code, is_banned
from utils.i18n import get_text

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
    
    text = get_text('panel_title', lang, 
                   username=username,
                   user_id=user_id,
                   balance=db_user.diamonds)

    keyboard = [
        [InlineKeyboardButton(get_text('buy_button', lang), callback_data='recharge')],
        [InlineKeyboardButton(get_text('referral_button', lang), callback_data='referral')],
        [InlineKeyboardButton(get_text('daily_button', lang), callback_data='daily')],
        [InlineKeyboardButton(get_text('process_button', lang), callback_data='process')]
    ]
    
    if db_user.is_admin:
        keyboard.append([InlineKeyboardButton("🛡️ Admin Panel", callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')