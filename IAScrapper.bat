@echo off
:: %~dp0 es la ruta de la carpeta donde reside este script
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo 🚀 Activando Entorno Virtual...
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo ⚠️ No se encontró la carpeta venv. Asegúrate de haberla creado.
    pause
    exit
)

echo 🤖 Lanzando Suite AI News Curator...
python run_all.py

pause