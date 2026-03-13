from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_user, get_user_by_id, add_diamonds, make_admin, ban_user, unban_user, get_all_users, is_admin
from utils.i18n import get_text

WAITING_FOR_USER_ID, WAITING_FOR_AMOUNT = range(2)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.edit_message_text(get_text('admin_not_admin', 'en'))
        return
    
    db_user = get_user(user_id)
    lang = db_user.language
    
    text = "🛡️ **Admin Control Panel**\n\nSelect an option:"
    
    keyboard = [
        [InlineKeyboardButton(get_text('admin_add_diamonds', lang), callback_data='admin_add_diamonds')],
        [InlineKeyboardButton(get_text('admin_make_admin', lang), callback_data='admin_make_admin')],
        [InlineKeyboardButton(get_text('admin_ban_user', lang), callback_data='admin_ban_user')],
        [InlineKeyboardButton(get_text('admin_unban_user', lang), callback_data='admin_unban_user')],
        [InlineKeyboardButton(get_text('admin_list_users', lang), callback_data='admin_list_users')],
        [InlineKeyboardButton(get_text('back_button', lang), callback_data='panel')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def admin_add_diamonds_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_text('admin_not_admin', 'en'))
        return ConversationHandler.END
    
    db_user = get_user(user_id)
    lang = db_user.language
    
    await query.edit_message_text(get_text('admin_enter_id', lang))
    return WAITING_FOR_USER_ID

async def admin_add_diamonds_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_user_id = int(update.message.text.strip())
        context.user_data['target_user_id'] = target_user_id
        
        db_user = get_user(update.effective_user.id)
        lang = db_user.language
        
        await update.message.reply_text(get_text('admin_enter_amount', lang))
        return WAITING_FOR_AMOUNT
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Please enter a number.")
        return WAITING_FOR_USER_ID

async def admin_add_diamonds_get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.strip())
        target_user_id = context.user_data['target_user_id']
        
        target_user = get_user_by_id(target_user_id)
        if not target_user:
            await update.message.reply_text(get_text('admin_user_not_found', 'en'))
            return ConversationHandler.END
        
        new_balance = add_diamonds(target_user_id, amount)
        
        db_user = get_user(update.effective_user.id)
        lang = db_user.language
        await update.message.reply_text(
            get_text('admin_diamonds_added', lang, amount=amount, user_id=target_user_id, balance=new_balance)
        )
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"✨ You received {amount}💎 from an admin!\n\nNew balance: {new_balance}💎"
            )
        except:
            pass
        
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please enter a number.")
        return WAITING_FOR_AMOUNT

async def admin_make_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_text('admin_not_admin', 'en'))
        return
    
    await query.edit_message_text("👑 Enter the user ID to make admin:")
    return WAITING_FOR_USER_ID

async def admin_make_admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_user_id = int(update.message.text.strip())
        
        target_user = get_user_by_id(target_user_id)
        if not target_user:
            await update.message.reply_text(get_text('admin_user_not_found', 'en'))
            return ConversationHandler.END
        
        if make_admin(target_user_id):
            await update.message.reply_text(get_text('admin_now_admin', 'en', user_id=target_user_id))
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="👑 Congratulations! You are now an admin of NitroPix bot."
                )
            except:
                pass
        else:
            await update.message.reply_text(get_text('admin_already_admin', 'en'))
        
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Please enter a number.")
        return WAITING_FOR_USER_ID

async def admin_ban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_text('admin_not_admin', 'en'))
        return
    
    await query.edit_message_text("🚫 Enter the user ID to ban:")
    return WAITING_FOR_USER_ID

async def admin_ban_user_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_user_id = int(update.message.text.strip())
        
        target_user = get_user_by_id(target_user_id)
        if not target_user:
            await update.message.reply_text(get_text('admin_user_not_found', 'en'))
            return ConversationHandler.END
        
        if ban_user(target_user_id):
            await update.message.reply_text(get_text('admin_user_banned', 'en', user_id=target_user_id))
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="🚫 You have been banned from using NitroPix bot. Contact @danyvg56 if you think this is a mistake."
                )
            except:
                pass
        else:
            await update.message.reply_text(get_text('admin_user_banned_error', 'en'))
        
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Please enter a number.")
        return WAITING_FOR_USER_ID

async def admin_unban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_text('admin_not_admin', 'en'))
        return
    
    await query.edit_message_text("✅ Enter the user ID to unban:")
    return WAITING_FOR_USER_ID

async def admin_unban_user_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_user_id = int(update.message.text.strip())
        
        target_user = get_user_by_id(target_user_id)
        if not target_user:
            await update.message.reply_text(get_text('admin_user_not_found', 'en'))
            return ConversationHandler.END
        
        if unban_user(target_user_id):
            await update.message.reply_text(get_text('admin_user_unbanned', 'en', user_id=target_user_id))
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="✅ You have been unbanned from NitroPix bot. You can now use it again."
                )
            except:
                pass
        else:
            await update.message.reply_text("❌ User is not banned.")
        
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Invalid ID. Please enter a number.")
        return WAITING_FOR_USER_ID

async def admin_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_text('admin_not_admin', 'en'))
        return
    
    users = get_all_users()
    
    text = "📋 **User List**\n\n"
    for user in users[:50]:
        admin_status = "👑" if user.is_admin else ""
        banned_status = "🚫" if user.is_banned else ""
        text += f"{admin_status}{banned_status} ID: `{user.telegram_id}` | {user.first_name or 'No name'} | 💎{user.diamonds}\n"
    
    if len(users) > 50:
        text += f"\n... and {len(users) - 50} more users."
    
    keyboard = [[InlineKeyboardButton(get_text('back_button', 'en'), callback_data='admin_panel')]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END