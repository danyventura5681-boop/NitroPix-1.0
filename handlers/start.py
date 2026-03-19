from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import database as db


# ==============================
# START COMMAND
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # Crear usuario automáticamente
    db.get_user(user.id)

    credits = db.get_credits(user.id)

    keyboard = [
        [InlineKeyboardButton("🎨 Efectos", callback_data="menu_effects")],
        [InlineKeyboardButton("💳 Créditos", callback_data="menu_credits")],
    ]

    await update.message.reply_text(
        f"🔥 Bienvenido a NitroPix Lite\n\n"
        f"✨ Créditos disponibles: {credits}\n\n"
        "Envía una foto y aplica efectos IA.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ==============================
# BUTTON HANDLER
# ==============================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "menu_credits":

        user_id = query.from_user.id
        credits = db.get_credits(user_id)

        await query.edit_message_text(
            f"💳 Créditos actuales: {credits}\n\n"
            "Cada efecto consume 1 crédito."
        )

    elif query.data == "menu_effects":

        keyboard = [
            [
                InlineKeyboardButton(
                    "✨ Próximamente",
                    callback_data="effect_comingsoon",
                )
            ]
        ]

        await query.edit_message_text(
            "🎨 Selecciona un efecto:",
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