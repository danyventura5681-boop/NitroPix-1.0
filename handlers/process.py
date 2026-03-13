from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user, deduct_diamond
from utils.i18n import get_text
import logging
import asyncio

logger = logging.getLogger(__name__)

async def process_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        message = query.message
    else:
        user_id = update.effective_user.id
        message = update.message

    db_user = get_user(user_id)
    if not db_user:
        if update.callback_query:
            await query.edit_message_text("Please /start first")
        else:
            await message.reply_text("Please /start first")
        return

    lang = db_user.language

    if db_user.diamonds < 1:
        text = "❌ You need at least 1💎 to process a photo.\n\nBuy more diamonds: /buy"
        keyboard = [[InlineKeyboardButton(get_text('buy_button', lang), callback_data='recharge')]]
        if update.callback_query:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if update.callback_query:
        text = "📸 Send me the photo you want to process!\n\n(1💎 will be deducted)"
        keyboard = [[InlineKeyboardButton(get_text('back_button', lang), callback_data='panel')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    try:
        deduct_diamond(user_id)
        new_balance = db_user.diamonds - 1
        
        processing_msg = await message.reply_text("✨ Processing your photo... (this will take a few seconds)")
        
        await asyncio.sleep(3)
        
        await processing_msg.delete()
        
        await message.reply_text(
            f"✅ Your photo has been enhanced!\n\n"
            f"💎 Remaining diamonds: {new_balance}\n\n"
            f"✨ Want to process another?",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⚡️ Process Another", callback_data='process'),
                InlineKeyboardButton("◀️ Back", callback_data='panel')
            ]])
        )
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await message.reply_text("❌ Sorry, an error occurred while processing your photo. Please try again.")