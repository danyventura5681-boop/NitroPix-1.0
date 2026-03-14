#!/usr/bin/env bash
# render-build.sh - Sin apt-get (compatible con plan Free)

set -e
echo "=== Iniciando build en Render (plan Free) ==="

# Actualizar pip
echo "=== Actualizando pip ==="
pip install --upgrade pip

# Instalar dependencias (forzar uso de wheels)
echo "=== Instalando dependencias con wheels ==="
pip install --only-binary=:all: Pillow==10.1.0
pip install -r requirements.txt

# Verificar instalación
echo "=== Verificando instalación ==="
python -c "from PIL import Image; print('✅ Pillok instalado correctamente')" || echo "❌ Error con Pillow"

echo "=== Build completado exitosamente ==="