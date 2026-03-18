from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db


# =====================================
# COMANDO /START
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Crear usuario si no existe
    db.create_user(user.id)

    lang = db.get_language(user.id)

    if lang == "es":
        text = "✨ Bienvenido a NitroPix\n\nSelecciona una opción:"
        keyboard = [
            [InlineKeyboardButton("🎨 Efectos", callback_data="menu_effects")],
            [InlineKeyboardButton("💎 Créditos", callback_data="menu_credits")],
            [InlineKeyboardButton("🌎 Idioma", callback_data="menu_language")],
        ]
    else:
        text = "✨ Welcome to NitroPix\n\nChoose an option:"
        keyboard = [
            [InlineKeyboardButton("🎨 Effects", callback_data="menu_effects")],
            [InlineKeyboardButton("💎 Credits", callback_data="menu_credits")],
            [InlineKeyboardButton("🌎 Language", callback_data="menu_language")],
        ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =====================================
# BOTONES DEL MENÚ
# =====================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    lang = db.get_language(user_id)

    # ===== MENÚ EFECTOS =====
    if query.data == "menu_effects":

        if lang == "es":
            text = "🎨 Selecciona un efecto:"
        else:
            text = "🎨 Select an effect:"

        keyboard = [
            [InlineKeyboardButton("🧑 Anime Avatar", callback_data="effect_avatar")],
            [InlineKeyboardButton("🧸 Action Figure", callback_data="effect_figura")],
            [InlineKeyboardButton("✏️ Manga", callback_data="effect_dibujo")],
            [InlineKeyboardButton("🎬 Cinemático", callback_data="effect_artistico")],
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== MENÚ CRÉDITOS =====
    elif query.data == "menu_credits":
        user = db.get_user(user_id)
        credits = user["credits"]

        if lang == "es":
            text = f"💎 Tienes {credits} créditos."
        else:
            text = f"💎 You have {credits} credits."

        await query.edit_message_text(text)

    # ===== MENÚ IDIOMA =====
    elif query.data == "menu_language":

        keyboard = [
            [InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")],
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        ]

        await query.edit_message_text(
            "🌎 Select language:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== CAMBIO DE IDIOMA =====
    elif query.data.startswith("lang_"):
        new_lang = query.data.split("_")[1]
        db.set_language(user_id, new_lang)

        msg = "✅ Idioma actualizado." if new_lang == "es" else "✅ Language updated."

        await query.edit_message_text(msg)


# =====================================
# SELECTOR DE EFECTOS (NUEVO)
# =====================================

async def effect_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Guarda el efecto seleccionado por el usuario
    para usarlo cuando envíe la foto.
    """

    query = update.callback_query
    await query.answer()

    effect_map = {
        "effect_avatar": "anime",
        "effect_figura": "action_figure",
        "effect_dibujo": "manga",
        "effect_artistico": "cinematic",
    }

    selected_effect = effect_map.get(query.data)

    if not selected_effect:
        return

    # Guardar efecto seleccionado
    context.user_data["selected_effect"] = selected_effect

    lang = db.get_language(query.from_user.id)

    if lang == "es":
        msg = "📸 Perfecto. Ahora envía una foto."
    else:
        msg = "📸 Perfect. Now send a photo."

    await query.edit_message_text(msg)