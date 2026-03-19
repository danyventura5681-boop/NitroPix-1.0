from telegram import Update
from telegram.ext import ContextTypes

# ==============================
# IMPORTAR HANDLERS REALES
# ==============================

from handlers.start import (
    start,
    button_handler,
    effect_selector,
)

from handlers.process import process_menu
from handlers.daily import daily_reward
from handlers.recharge import recharge_menu
from handlers.referral import referral_menu
from handlers.admin import admin_panel


# ==============================
# CALLBACK ROUTER CENTRAL
# ==============================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Router central para TODOS los botones del bot
    """

    query = update.callback_query
    await query.answer()

    data = query.data

    # ==============================
    # EFFECT SELECTOR (NUEVO SISTEMA)
    # ==============================
    if data.startswith("effect_"):
        await effect_selector(update, context)

    # ==============================
    # PANEL / BOTONES GENERALES
    # ==============================
    elif data == "panel":
        await button_handler(update, context)

    # ==============================
    # PROCESS PHOTO
    # ==============================
    elif data == "process":
        await process_menu(update, context)

    # ==============================
    # DAILY REWARD
    # ==============================
    elif data == "daily":
        await daily_reward(update, context)

    # ==============================
    # RECHARGE
    # ==============================
    elif data == "recharge":
        await recharge_menu(update, context)

    # ==============================
    # REFERRAL
    # ==============================
    elif data == "referral":
        await referral_menu(update, context)

    # ==============================
    # ADMIN PANEL
    # ==============================
    elif data == "admin_panel":
        await admin_panel(update, context)

    # ==============================
    # FALLBACK
    # ==============================
    else:
        await query.answer("⚠️ Acción no reconocida", show_alert=True)