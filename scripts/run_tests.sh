#!/bin/bash
set -e

if [ ! -f .env ]; then
    echo "Error: no existe el archivo .env"
    exit 1
fi

set -a
source .env
set +a

echo "Iniciando pruebas..."
python.exe -m pytest tests/ -v

echo "Pruebas finalizadas correctamente."
