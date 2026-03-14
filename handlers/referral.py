from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user
from utils.i18n import get_text

async def referral_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        return

    lang = db_user.language
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{db_user.referral_code}"
    
    text = (
        "🚀 **¡Invita amigos y gana!** 🚀\n\n"
        f"🔗 **Tu enlace personal:**\n`{ref_link}`\n\n"
        "🤝 **Por cada amigo que se una y use el bot, ¡RECIBES 3💎!**\n\n"
        "📤 **Comparte este enlace y empieza a ganar diamantes extras.**"
    )

    keyboard = [[InlineKeyboardButton("◀️ Volver al Panel", callback_data='panel')]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')