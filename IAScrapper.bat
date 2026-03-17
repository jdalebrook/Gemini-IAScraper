@echo off
:: %~dp0 es la ruta de la carpeta donde reside este script
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo 🚀 Iniciando entorno virtual...
call venv\Scripts\activate

echo 🤖 Ejecutando AI News Curator...
python run_all.py

pause