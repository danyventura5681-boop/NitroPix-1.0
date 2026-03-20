from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db
from utils.i18n import get_text


# ==============================
# START COMMAND
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # Crear usuario si no existe
    user_data = db.get_user(user.id)

    credits = db.get_credits(user.id)

    # idioma seguro (fallback español)
    lang = "es"
    if isinstance(user_data, dict):
        lang = user_data.get("language", "es")

    # teclado principal
    keyboard = [
        [
            InlineKeyboardButton(
                get_text("process_button", lang),
                callback_data="process",
            )
        ],
        [
            InlineKeyboardButton(
                "📋 Panel",
                callback_data="panel",
            )
        ],
    ]

    await update.message.reply_text(
        get_text("welcome", lang),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==============================
# PANEL HANDLER
# ==============================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_data = db.get_user(user_id)
    credits = db.get_credits(user_id)

    # idioma seguro
    lang = "es"
    if isinstance(user_data, dict):
        lang = user_data.get("language", "es")

    keyboard = [
        [
            InlineKeyboardButton(
                get_text("process_button", lang),
                callback_data="process",
            )
        ],
        [
            InlineKeyboardButton(
                get_text("recharge_title", lang),
                callback_data="recharge",
            )
        ],
        [
            InlineKeyboardButton(
                get_text("referral_button", lang),
                callback_data="referral",
            )
        ],
    ]

    await query.edit_message_text(
        get_text("panel_title", lang, username=query.from_user.first_name)
        + f"\n\n💎 {credits}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==============================
# EFFECT SELECTOR
# ==============================

async def effect_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_data = db.get_user(query.from_user.id)

    lang = "es"
    if isinstance(user_data, dict):
        lang = user_data.get("language", "es")

    await query.edit_message_text(
        "🚧 Los efectos estarán disponibles pronto."
    )