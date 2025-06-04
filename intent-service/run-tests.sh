#!/bin/bash
echo ">> Instalando pytest y dependencias de test"
pip install -r requirements.txt
echo ">> Ejecutando tests"
pytest --disable-warnings -q
