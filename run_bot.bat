@echo off
chcp 65001 > nul
title WhatsApp RPA Bot - Taller RPA Asignacion 2

echo ========================================================================
echo     UNIVERSIDAD DE CARABOBO - FACULTAD DE CIENCIAS Y TECNOLOGIA
echo              SISTEMAS DE INFORMACION - TALLER DE RPA
echo              ASIGNACION 2: BOT DE WHATSAPP WEB
echo ========================================================================
echo.

:: Verificar si PDM esta instalado
where pdm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] ERROR: PDM no se encuentra instalado o no esta en el PATH.
    echo Por favor instale PDM o agreguelo al PATH del sistema.
    echo.
    pause
    exit /b 1
)

:: Verificar e instalar dependencias si es necesario
if not exist ".venv" (
    echo [*] Detectada primera ejecucion. Instalando dependencias del proyecto con PDM...
    pdm install
    if %ERRORLEVEL% neq 0 (
        echo [!] ERROR al instalar las dependencias con PDM.
        pause
        exit /b 1
    )
    echo [*] Instalando navegadores de Playwright...
    pdm run playwright install chromium
)

echo [*] Iniciando Bot de WhatsApp con PDM...
echo.

pdm run python main.py %*

echo.
echo ========================================================================
echo Ejecucion finalizada. Presione cualquier tecla para cerrar la consola...
echo ========================================================================
pause > nul
