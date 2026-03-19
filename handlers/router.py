from telegram import Update
from telegram.ext import ContextTypes

# Importamos handlers existentes
from handlers.start import start, panel
from handlers.process import process_menu
from handlers.daily import daily_reward
from handlers.recharge import recharge_menu
from handlers.referral import referral_menu
from handlers.admin import admin_panel


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Router central para TODOS los botones"""

    query = update.callback_query
    data = query.data

    # =========================
    # PANEL
    # =========================
    if data == "panel":
        await panel(update, context)

    # =========================
    # PROCESS PHOTO
    # =========================
    elif data == "process":
        await process_menu(update, context)

    # =========================
    # DAILY REWARD
    # =========================
    elif data == "daily":
        await daily_reward(update, context)

    # =========================
    # RECHARGE
    # =========================
    elif data == "recharge":
        await recharge_menu(update, context)

    # =========================
    # REFERRAL
    # =========================
    elif data == "referral":
        await referral_menu(update, context)

    # =========================
    # ADMIN PANEL
    # =========================
    elif data == "admin_panel":
        await admin_panel(update, context)

    else:
        await query.answer("⚠️ Acción no reconocida")