#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ConversationHandler
)
from handlers.start import start, handle_language_selection, panel_menu
from handlers.referral import referral_code
from handlers.daily import daily_reward
from handlers.recharge import recharge_menu, handle_plan_selection, other_payment_methods
from handlers.process import process_photo
from handlers.admin import (
    admin_panel, admin_add_diamonds_start, admin_add_diamonds_get_id,
    admin_add_diamonds_get_amount, admin_make_admin_start, admin_make_admin_process,
    admin_ban_user_start, admin_ban_user_process, admin_unban_user_start,
    admin_unban_user_process, admin_list_users, cancel,
    WAITING_FOR_USER_ID, WAITING_FOR_AMOUNT
)
from config import TOKEN
import logging

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def main():
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    
    # Callback query handlers
    app.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(panel_menu, pattern="^panel$"))
    app.add_handler(CallbackQueryHandler(referral_code, pattern="^referral$"))
    app.add_handler(CallbackQueryHandler(daily_reward, pattern="^daily$"))
    app.add_handler(CallbackQueryHandler(recharge_menu, pattern="^recharge$"))
    app.add_handler(CallbackQueryHandler(handle_plan_selection, pattern="^plan_"))
    app.add_handler(CallbackQueryHandler(other_payment_methods, pattern="^other_payment$"))
    app.add_handler(CallbackQueryHandler(process_photo, pattern="^process$"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    
    # Conversation handlers para admin
    add_diamonds_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_diamonds_start, pattern="^admin_add_diamonds$")],
        states={
            WAITING_FOR_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_diamonds_get_id)],
            WAITING_FOR_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_add_diamonds_get_amount)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    make_admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_make_admin_start, pattern="^admin_make_admin$")],
        states={
            WAITING_FOR_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_make_admin_process)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    ban_user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_ban_user_start, pattern="^admin_ban_user$")],
        states={
            WAITING_FOR_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_ban_user_process)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    unban_user_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_unban_user_start, pattern="^admin_unban_user$")],
        states={
            WAITING_FOR_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_unban_user_process)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    list_users_handler = CallbackQueryHandler(admin_list_users, pattern="^admin_list_users$")
    
    app.add_handler(add_diamonds_conv)
    app.add_handler(make_admin_conv)
    app.add_handler(ban_user_conv)
    app.add_handler(unban_user_conv)
    app.add_handler(list_users_handler)
    
    # Message handlers (para fotos)
    app.add_handler(MessageHandler(filters.PHOTO, process_photo))

    print("✨ NitroPix Bot iniciado correctamente!")
    print("👑 Admin user: @danyvg56")
    app.run_polling()

if __name__ == "__main__":
    main()