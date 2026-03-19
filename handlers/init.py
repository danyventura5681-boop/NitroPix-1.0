from telegram.ext import Application

# importar módulos
from . import start
from . import effects
from . import admin
from . import daily
from . import referral
from . import recharge
from . import process


def register_handlers(app: Application):
    """
    Registra TODOS los handlers del bot
    """

    # START
    app.add_handler(start.get_handlers())

    # EFFECTS
    app.add_handler(effects.get_handlers())

    # ADMIN
    app.add_handler(admin.get_handlers())

    # DAILY
    app.add_handler(daily.get_handlers())

    # REFERRAL
    app.add_handler(referral.get_handlers())

    # RECHARGE
    app.add_handler(recharge.get_handlers())

    # PROCESS (photos / IA)
    app.add_handler(process.get_handlers())