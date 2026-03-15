from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database import get_user


# ===============================
# MENU DE EFECTOS NITROPIX
# ===============================

async def show_effects_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        await update.message.reply_text("❌ Usuario no encontrado.")
        return

    diamonds = user["diamonds"]

    text = f"""
🎨 Elige un efecto mágico:

Tus 💎: {diamonds}

⚡ Powered by: NitroPix
"""

    keyboard = [

        [
            InlineKeyboardButton("✨ Mejorar a HD - 1💎", callback_data="effect_hd"),
            InlineKeyboardButton("✏️ Convertir en Dibujo - 1💎", callback_data="effect_drawing")
        ],

        [
            InlineKeyboardButton("📖 Convertir en Manga - 2💎", callback_data="effect_manga"),
            InlineKeyboardButton("🎭 Crear Avatar - 2💎", callback_data="effect_avatar")
        ],

        [
            InlineKeyboardButton("🦸 Figura de Acción - 2💎", callback_data="effect_action"),
            InlineKeyboardButton("🎨 Diseño Artístico - 2💎", callback_data="effect_artistic")
        ],

        [
            InlineKeyboardButton(
                "🚀 Invitar Amigos para Conseguir 💎",
                callback_data="invite"
            )
        ],

        [
            InlineKeyboardButton("🏠 Panel Principal", callback_data="home")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )
