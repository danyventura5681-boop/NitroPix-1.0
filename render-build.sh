#!/usr/bin/env bash
set -e
echo "=== Iniciando build en Render ==="

# Actualizar pip
echo "=== Actualizando pip ==="
pip install --upgrade pip wheel setuptools

# Instalar Pillow primero con opciones específicas
echo "=== Instalando Pillow desde wheel ==="
pip install --only-binary=:all: Pillow==9.5.0 || pip install Pillow==9.5.0

# Instalar resto de dependencias
echo "=== Instalando resto de dependencias ==="
pip install -r requirements.txt

echo "=== Verificación ==="
python -c "from PIL import Image; print('✅ Pillow instalado correctamente')"

echo "=== Build completado ==="