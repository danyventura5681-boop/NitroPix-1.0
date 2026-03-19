from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_user, deduct_diamond
from utils.i18n import get_text

import logging
import asyncio

logger = logging.getLogger(__name__)


# =====================================================
# PROCESS MENU (FIX FOR ROUTER IMPORT)
# =====================================================

async def process_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Alias para evitar error de import en router.py
    """
    await process_photo(update, context)


# =====================================================
# PROCESS PHOTO MENU
# =====================================================

async def process_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Detectar si viene de botón o mensaje
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        message = query.message
    else:
        user_id = update.effective_user.id
        message = update.message

    # Obtener usuario
    db_user = get_user(user_id)

    if not db_user:
        await message.reply_text("Please /start first")
        return

    lang = db_user.get("language", "en")
    credits = db_user.get("credits", 0)

    # =============================
    # SIN CRÉDITOS
    # =============================
    if credits < 1:
        text = "❌ You need at least 1 credit to process a photo.\nBuy more with /buy"

        keyboard = [
            [InlineKeyboardButton("💎 Buy", callback_data="recharge")]
        ]

        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # =============================
    # PEDIR FOTO
    # =============================
    if update.callback_query:

        text = "📸 Send me the photo you want to process.\n\n💎 1 credit will be deducted."

        keyboard = [
            [InlineKeyboardButton("⬅ Back", callback_data="panel")]
        ]

        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # =============================
    # PROCESAMIENTO SIMULADO
    # =============================
    try:
        deduct_diamond(user_id, 1)

        processing_msg = await message.reply_text(
            "✨ Processing your photo... (this may take a few seconds)"
        )

        await asyncio.sleep(3)

        await processing_msg.delete()

        new_balance = get_user(user_id).get("credits", 0)

        await message.reply_text(
            f"✅ Photo processed successfully!\n\n"
            f"💎 Remaining credits: {new_balance}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Process Another", callback_data="process")],
                [InlineKeyboardButton("⬅ Back", callback_data="panel")]
            ])
        )

    except Exception as e:
        logger.error(f"Error processing photo: {e}")

        await message.reply_text(
            "❌ An error occurred while processing your photo. Please try again."
        )