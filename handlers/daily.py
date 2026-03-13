from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user, can_claim_daily, set_daily_claimed, add_diamonds
from utils.i18n import get_text

async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        return

    lang = db_user.language
    can_claim, hours = can_claim_daily(user_id)

    if can_claim:
        new_balance = add_diamonds(user_id, 0.5)
        set_daily_claimed(user_id)
        text = get_text('daily_success', lang, balance=new_balance)
    else:
        text = get_text('daily_already_claimed', lang, hours=hours)

    keyboard = [[InlineKeyboardButton(get_text('back_button', lang), callback_data='panel')]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')