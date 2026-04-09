@echo off
echo.
echo  ==========================================
echo   Skully News - Build para Windows
echo  ==========================================
echo.

python -m PyInstaller skully.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo  ERROR: el build ha fallado. Revisa los mensajes anteriores.
    pause
    exit /b 1
)

echo.
echo  Copiando configuracion de feeds...
xcopy /E /I /Y config dist\Skully\config >nul

echo  Creando carpeta de datos...
if not exist dist\Skully\data mkdir dist\Skully\data

echo  Copiando plantilla .env...
copy /Y .env.example dist\Skully\.env.example >nul

echo.
echo  ==========================================
echo   Build completado en:  dist\Skully\
echo  ==========================================
echo.
echo  Para distribuir:
echo    1. Comprime dist\Skully\ en un .zip
echo    2. El usuario renombra .env.example a .env
echo       y pega su GEMINI_API_KEY
echo    3. Doble clic en Skully.exe
echo.
pause
