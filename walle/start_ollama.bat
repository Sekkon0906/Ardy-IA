@echo off
echo ========================================
echo  Iniciando Ollama Server
echo ========================================
echo.
echo Este servidor debe mantenerse abierto
echo No cierres esta ventana
echo.

REM Verificar si ya está corriendo
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo [!] Ollama ya esta corriendo en otro proceso
    pause
    exit /b 0
)

REM Iniciar Ollama
echo Iniciando Ollama en http://localhost:11434
echo.
ollama serve