from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import database as db
from utils.i18n import get_text
from datetime import datetime

WAITING_FOR_USER_ID, WAITING_FOR_AMOUNT = range(2)


# ==============================
# ADMIN PANEL
# ==============================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not db.is_admin(user_id):
        await query.edit_message_text(get_text('admin_not_admin', 'en'))
        return

    db_user = db.get_user(user_id)
    lang = db_user.get("language", "en")

    stats = db.get_user_stats()

    text = (
        "🛡️ **Panel de Administrador**\n\n"
        "📊 **Estadísticas de Usuarios:**\n"
        f"👥 **Totales:** {stats['total']}\n"
        f"📅 **Último mes:** +{stats['last_month']}\n"
        f"📆 **Última semana:** +{stats['last_week']}\n"
        f"⏰ **Últimas 48h:** +{stats['last_48h']}\n"
        f"⚡ **Activos 48h:** {stats['active_48h']}\n\n"
        "🛠️ **Acciones:**"
    )

    keyboard = [
        [InlineKeyboardButton("📊 Actualizar Estadísticas", callback_data='admin_stats')],
        [InlineKeyboardButton(get_text('admin_add_diamonds', lang), callback_data='admin_add_diamonds')],
        [InlineKeyboardButton(get_text('admin_make_admin', lang), callback_data='admin_make_admin')],
        [InlineKeyboardButton(get_text('admin_ban_user', lang), callback_data='admin_ban_user')],
        [InlineKeyboardButton(get_text('admin_unban_user', lang), callback_data='admin_unban_user')],
        [InlineKeyboardButton(get_text('admin_list_users', lang), callback_data='admin_list_users')],
        [InlineKeyboardButton(get_text('back_button', lang), callback_data='panel')]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


# ==============================
# STATS
# ==============================

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not db.is_admin(user_id):
        await query.edit_message_text(get_text('admin_not_admin', 'en'))
        return

    stats = db.get_user_stats()

    text = (
        "📊 **Estadísticas Actualizadas:**\n\n"
        f"👥 **Usuarios totales:** {stats['total']}\n"
        f"📅 **Último mes:** +{stats['last_month']}\n"
        f"📆 **Última semana:** +{stats['last_week']}\n"
        f"⏰ **Últimas 48h:** +{stats['last_48h']}\n"
        f"⚡ **Activos últimas 48h:** {stats['active_48h']}\n\n"
        f"🕒 *Actualizado: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC*"
    )

    keyboard = [[InlineKeyboardButton("◀️ Volver", callback_data='admin_panel')]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


# ==============================
# ADD DIAMONDS FLOW
# ==============================

async def admin_add_diamonds_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if not db.is_admin(user_id):
        return ConversationHandler.END

    await query.edit_message_text("Enter user ID:")
    return WAITING_FOR_USER_ID


async def admin_add_diamonds_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        context.user_data['target_user_id'] = int(update.message.text.strip())
        await update.message.reply_text("Enter amount:")
        return WAITING_FOR_AMOUNT

    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")
        return WAITING_FOR_USER_ID


async def admin_add_diamonds_get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        amount = float(update.message.text.strip())
        target_user_id = context.user_data['target_user_id']

        target_user = db.get_user(target_user_id)

        if not target_user:
            await update.message.reply_text("User not found.")
            return ConversationHandler.END

        new_balance = db.add_diamonds(target_user_id, amount)

        await update.message.reply_text(
            f"✅ Added {amount}💎 to {target_user_id}\nNew balance: {new_balance}"
        )

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"✨ You received {amount}💎 from an admin!\nNew balance: {new_balance}"
            )
        except:
            pass

        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("❌ Invalid amount.")
        return WAITING_FOR_AMOUNT


# ==============================
# CANCEL
# ==============================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END