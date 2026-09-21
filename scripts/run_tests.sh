#!/bin/bash
# Script para cargar secretos de forma segura y ejecutar pruebas

echo "Cargando variables de entorno desde .env..."
# Exporta las variables del .env ignorando los comentarios
export $(grep -v '^#' .env | xargs)

echo "Variables cargadas. Iniciando pruebas de seguridad y acceso..."
pytest tests/ -v

echo "Pruebas finalizadas."