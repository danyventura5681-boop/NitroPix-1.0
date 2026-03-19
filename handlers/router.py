from telegram import Update
from telegram.ext import ContextTypes

import logging

# ==============================
# LOGGER
# ==============================

logger = logging.getLogger(__name__)


# ==============================
# IMPORTAR HANDLERS
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

    # Seguridad extra (evita crash raro)
    if not query:
        logger.warning("Callback sin query recibido")
        return

    data = query.data

    try:
        # responder callback inmediatamente (evita timeout Telegram)
        await query.answer()

        logger.info(f"Callback recibido: {data}")

        # ==============================
        # EFFECT SELECTOR
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
            logger.warning(f"Callback desconocido: {data}")
            await query.answer(
                "⚠️ Acción no reconocida",
                show_alert=True
            )

    except Exception as e:
        logger.exception("Error en callback_router")

        # evita que el bot muera en Render
        try:
            await query.answer(
                "❌ Ocurrió un error interno",
                show_alert=True
            )
        except Exception:
            pass