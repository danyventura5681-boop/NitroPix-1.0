#!/usr/bin/env bash
set -e
echo "=== Iniciando build en Render ==="

# Actualizar pip
echo "=== Actualizando pip ==="
pip install --upgrade pip

# Instalar dependencias
echo "=== Instalando dependencias ==="
pip install -r requirements.txt

echo "=== Verificando instalación ==="
python -c "from PIL import Image; print('✅ Pillow 9.5.0 instalado correctamente')"

echo "=== Build completado ==="