#!/usr/bin/env bash
# Build script para Render
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos automáticamente
echo "Inicializando base de datos..."
python init_db.py
echo "Base de datos lista!"
