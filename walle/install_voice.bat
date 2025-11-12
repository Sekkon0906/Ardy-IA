@echo off
chcp 65001 >nul
cls

echo ════════════════════════════════════════
echo  WALL-E AI - Instalador de Voz
echo  Speech-to-Text + Text-to-Speech
echo ════════════════════════════════════════
echo.
echo  Este instalador agregará:
echo  ✓ Faster Whisper (transcripción)
echo  ✓ Coqui TTS (síntesis de voz)
echo  ✓ PyDub (procesamiento audio)
echo.
echo  Tiempo estimado: 5-10 minutos
echo  Espacio requerido: ~2 GB
echo ════════════════════════════════════════
echo.
pause

REM Verificar entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [X] Entorno virtual no encontrado
    echo     Ejecuta install.bat primero
    pause
    exit /b 1
)

echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [X] Error al activar entorno
    pause
    exit /b 1
)
echo [OK] Entorno activado
echo.

echo ════════════════════════════════════════
echo  PASO 1: Faster Whisper (STT)
echo ════════════════════════════════════════
echo.
echo [*] Instalando faster-whisper...
echo     (Esto puede tardar 2-3 minutos)
echo.

pip install faster-whisper==1.0.3 --quiet
if %errorlevel% neq 0 (
    echo [!] Faster-whisper falló, intentando con flags de compatibilidad...
    pip install faster-whisper==1.0.3 --no-cache-dir
    if %errorlevel% neq 0 goto install_error
)
echo [OK] Faster Whisper instalado
echo.

echo ════════════════════════════════════════
echo  PASO 2: PyDub (Audio Processing)
echo ════════════════════════════════════════
echo.
echo [*] Instalando pydub y soundfile...
pip install pydub==0.25.1 soundfile==0.12.1 --quiet
if %errorlevel% neq 0 goto install_error
echo [OK] PyDub instalado
echo.

echo ════════════════════════════════════════
echo  PASO 3: Coqui TTS (Text-to-Speech)
echo ════════════════════════════════════════
echo.
echo [!] ADVERTENCIA: TTS es OPCIONAL y pesado (~1.5 GB)
echo.
echo     Si solo quieres transcripción (voz a texto),
echo     puedes omitir este paso.
echo.
choice /C SN /M "¿Instalar TTS (S=Si, N=No)"
if %errorlevel% equ 2 goto skip_tts

echo.
echo [*] Instalando Coqui TTS...
echo     (Esto puede tardar 5-10 minutos y descargar ~1.5 GB)
echo     NO cierres esta ventana...
echo.

pip install TTS==0.22.0 --quiet
if %errorlevel% neq 0 (
    echo [!] TTS falló, intentando con --no-cache-dir...
    pip install TTS==0.22.0 --no-cache-dir
    if %errorlevel% neq 0 (
        echo [!] TTS no se pudo instalar
        echo     La app funcionará sin síntesis de voz
        goto skip_tts
    )
)
echo [OK] Coqui TTS instalado
goto verify

:skip_tts
echo [*] TTS omitido - solo tendrás transcripción (voz a texto)
echo.

:verify
echo ════════════════════════════════════════
echo  VERIFICACIÓN DE MÓDULOS
echo ════════════════════════════════════════
echo.

echo [*] Verificando instalación...
echo.

python -c "import faster_whisper; print('[OK] Faster Whisper')" 2>nul || echo [X] Faster Whisper FALLO
python -c "import pydub; print('[OK] PyDub')" 2>nul || echo [X] PyDub FALLO
python -c "import soundfile; print('[OK] SoundFile')" 2>nul || echo [X] SoundFile FALLO
python -c "from TTS.api import TTS; print('[OK] Coqui TTS')" 2>nul || echo [!] TTS no disponible (opcional)

echo.
echo ════════════════════════════════════════
echo  TEST DE FUNCIONALIDAD
echo ════════════════════════════════════════
echo.

echo [*] Probando STT Service...
python -c "from backend.services.stt_service import stt_service; stt_service.load_model(); print('[OK] STT cargado correctamente' if stt_service.is_loaded else '[X] STT no cargó')" 2>nul
if %errorlevel% neq 0 (
    echo [!] STT Service tiene problemas
    echo     Detalles:
    python -c "from backend.services.stt_service import stt_service; stt_service.load_model()"
)
echo.

echo [*] Probando TTS Service...
python -c "from backend.services.tts_service import tts_service; tts_service.load_model(); print('[OK] TTS cargado correctamente' if tts_service.is_loaded else '[!] TTS no disponible (es opcional)')" 2>nul
echo.

echo ════════════════════════════════════════
echo  INSTALACIÓN COMPLETADA
echo ════════════════════════════════════════
echo.
echo  Módulos de voz instalados:
echo  ✓ Faster Whisper (Speech-to-Text)
echo  ✓ PyDub (Audio Processing)
python -c "from TTS.api import TTS; print('  ✓ Coqui TTS (Text-to-Speech)')" 2>nul || echo   - TTS no instalado (opcional)
echo.
echo ════════════════════════════════════════
echo  PRÓXIMOS PASOS
echo ════════════════════════════════════════
echo.
echo  1. Reinicia el servidor:
echo     start.bat
echo.
echo  2. La funcionalidad de voz estará disponible en:
echo     POST /voice (enviar audio, recibir respuesta)
echo.
echo  3. Formatos de audio soportados:
echo     - WAV, MP3, OGG, FLAC, M4A
echo     - Máximo: 10 MB por archivo
echo.
echo ════════════════════════════════════════
pause
exit /b 0

:install_error
echo.
echo ════════════════════════════════════════
echo  ERROR EN LA INSTALACIÓN
echo ════════════════════════════════════════
echo.
echo  Un módulo no se pudo instalar.
echo.
echo  Soluciones:
echo.
echo  1. INTERNET: Verifica tu conexión
echo  2. ESPACIO: Necesitas ~2 GB libres
echo  3. COMPILADOR: Instala Visual C++ Build Tools
echo     https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo.
echo  Para reintentar manualmente:
echo  1. call venv\Scripts\activate.bat
echo  2. pip install faster-whisper==1.0.3
echo  3. pip install pydub==0.25.1 soundfile==0.12.1
echo  4. pip install TTS==0.22.0 (opcional)
echo.
echo ════════════════════════════════════════
pause
exit /b 1
