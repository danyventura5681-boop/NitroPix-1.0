#!/usr/bin/env bash
# render-build.sh
# Script de compilación para Render que instala dependencias del sistema

set -e  # Salir si hay error

echo "=== Instalando dependencias del sistema para Pillow y OpenCV ==="
apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    && rm -rf /var/lib/apt/lists/*

echo "=== Actualizando pip ==="
pip install --upgrade pip

echo "=== Instalando dependencias de Python ==="
pip install -r requirements.txt

echo "=== Build completado exitosamente ==="