@echo off
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: ── Entorno virtual ────────────────────────────────────────────────────────────
echo [1/3] Verificando entorno virtual...
if not exist venv\Scripts\activate (
    echo     No existe venv. Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual. Asegurate de tener Python instalado.
        pause
        exit /b 1
    )
    echo     Entorno virtual creado.
)
call venv\Scripts\activate

:: ── Dependencias ──────────────────────────────────────────────────────────────
echo [2/3] Actualizando dependencias...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo     Dependencias OK.

:: ── Arranque ──────────────────────────────────────────────────────────────────
echo [3/3] Lanzando AI News Curator...
python run_all.py

pause