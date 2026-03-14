import os
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ No BOT_TOKEN found in environment variables")

# ===========================================
# 1. IMPORTAR TUS HANDLERS
# ===========================================
from handlers.start import start, handle_language_selection, panel_menu, ask_join_group, verify_group, skip_group
from handlers.referral import referral_code
from handlers.daily import daily_reward
from handlers.recharge import recharge_menu, handle_plan_selection, other_payment_methods
from handlers.effects import show_effects_menu, handle_effect_selection, process_effect
from handlers.admin import admin_panel, admin_stats, admin_add_diamonds_start, admin_make_admin_start, admin_ban_user_start, admin_unban_user_start, admin_list_users
from handlers.admin import WAITING_FOR_USER_ID, WAITING_FOR_AMOUNT, admin_add_diamonds_get_id, admin_add_diamonds_get_amount, admin_make_admin_process, admin_ban_user_process, admin_unban_user_process, cancel

# ===========================================
# 2. CONFIGURAR EL BOT
# ===========================================
telegram_app = Application.builder().token(TOKEN).build()

# Handlers básicos
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^lang_"))
telegram_app.add_handler(CallbackQueryHandler(panel_menu, pattern="^panel$"))
telegram_app.add_handler(CallbackQueryHandler(ask_join_group, pattern="^ask_join$"))
telegram_app.add_handler(CallbackQueryHandler(verify_group, pattern="^verify_group$"))
telegram_app.add_handler(CallbackQueryHandler(skip_group, pattern="^skip_group$"))
telegram_app.add_handler(CallbackQueryHandler(referral_code, pattern="^referral$"))
telegram_app.add_handler(CallbackQueryHandler(daily_reward, pattern="^daily$"))
telegram_app.add_handler(CallbackQueryHandler(recharge_menu, pattern="^recharge$"))
telegram_app.add_handler(CallbackQueryHandler(handle_plan_selection, pattern="^plan_"))
telegram_app.add_handler(CallbackQueryHandler(other_payment_methods, pattern="^other_payment$"))
telegram_app.add_handler(CallbackQueryHandler(show_effects_menu, pattern="^effects$"))
telegram_app.add_handler(CallbackQueryHandler(handle_effect_selection, pattern="^effect_"))
telegram_app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
telegram_app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
telegram_app.add_handler(MessageHandler(filters.PHOTO, process_effect))

# Conversation handlers
from telegram.ext import ConversationHandler
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

telegram_app.add_handler(add_diamonds_conv)
telegram_app.add_handler(make_admin_conv)
telegram_app.add_handler(ban_user_conv)
telegram_app.add_handler(unban_user_conv)
telegram_app.add_handler(CallbackQueryHandler(admin_list_users, pattern="^admin_list_users$"))

# ===========================================
# 3. SERVIDOR WEB MÍNIMO PARA RENDER
# ===========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        # Silenciar logs del servidor
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"✅ Servidor de salud corriendo en puerto {port}")
    server.serve_forever()

# ===========================================
# 4. INICIAR TODO
# ===========================================
def main():
    # Iniciar servidor web en un hilo separado
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Iniciar el bot
    logger.info("✨ Iniciando NitroPix Bot con polling...")
    telegram_app.run_polling()

if __name__ == "__main__":
    main()