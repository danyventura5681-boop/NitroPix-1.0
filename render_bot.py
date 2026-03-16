import os
from bot import main

PORT = int(os.environ.get("PORT", 8080))  # Render asigna el puerto
print(f"Iniciando NitroPix Lite en Render en puerto {PORT}")

if __name__ == "__main__":
    main()