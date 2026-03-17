import os
import subprocess
from typing import Any

from keep_alive import keep_alive
from bot import main
from cog import BasePredictor

# Mantener vivo el servicio
keep_alive()

PORT = int(os.environ.get("PORT", 8080))
print(f"Iniciando NitroPix Lite en Render en puerto {PORT}")


# Ejecutar normalmente si se corre como script
if __name__ == "__main__":
    main()


# ===== COG PREDICTOR (necesario para Cog) =====
class Predictor(BasePredictor):
    def setup(self):
        pass

    def predict(self) -> Any:
        subprocess.Popen(["python", "bot.py"])
        return "Bot started"