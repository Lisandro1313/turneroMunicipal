#!/usr/bin/env bash
# Build script para Render
set -o errexit

echo "==> Instalando dependencias..."
pip install -r requirements.txt

echo "==> Inicializando base de datos..."
python init_db.py || echo "Base de datos ya existe o error en inicialización"
echo "==> Build completado!"
