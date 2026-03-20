from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db


# ==============================
# START COMMAND
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    db.get_user(user.id)
    credits = db.get_credits(user.id)

    keyboard = [
        [InlineKeyboardButton("🎨 Efectos", callback_data="process")],
        [InlineKeyboardButton("💳 Panel", callback_data="panel")],
    ]

    await update.message.reply_text(
        f"🔥 Bienvenido a NitroPix Lite\n\n"
        f"✨ Créditos disponibles: {credits}\n\n"
        "Envía una foto y aplica efectos IA.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==============================
# PANEL HANDLER
# ==============================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    credits = db.get_credits(user_id)

    keyboard = [
        [InlineKeyboardButton("🎨 Efectos", callback_data="process")],
        [InlineKeyboardButton("💳 Recargar", callback_data="recharge")],
        [InlineKeyboardButton("🎁 Referidos", callback_data="referral")],
    ]

    await query.edit_message_text(
        f"🏠 Panel principal\n\n"
        f"💎 Créditos: {credits}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==============================
# EFFECT SELECTOR
# ==============================

async def effect_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🚧 Los efectos estarán disponibles pronto."
    )