from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user
from utils.i18n import get_text
from config import PLANS, TRX_ADDRESS, TRX_PER_USD

async def recharge_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        return

    lang = db_user.language
    text = get_text('recharge_title', lang)

    keyboard = []
    for key, plan in PLANS.items():
        trx_amount = plan['usd'] * TRX_PER_USD
        btn_text = get_text(f'plan_{key}', lang, usd=plan['usd'], trx=trx_amount)
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"plan_{key}")])
    
    keyboard.append([InlineKeyboardButton(get_text('other_payment', lang), callback_data='other_payment')])
    keyboard.append([InlineKeyboardButton(get_text('back_button', lang), callback_data='panel')])

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        return

    plan_key = query.data.split('_')[1]
    plan = PLANS.get(plan_key)
    if not plan:
        return

    lang = db_user.language
    trx_amount = plan['usd'] * TRX_PER_USD
    text = get_text('payment_instructions', lang, 
                   diamonds=plan['diamonds'],
                   trx=trx_amount, 
                   address=TRX_ADDRESS)

    keyboard = [[InlineKeyboardButton(get_text('back_button', lang), callback_data='panel')]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def other_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        return

    lang = db_user.language
    text = get_text('other_payment_text', lang)

    keyboard = [[InlineKeyboardButton(get_text('back_button', lang), callback_data='panel')]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')