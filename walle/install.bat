@echo off
chcp 65001 >nul
cls

echo ════════════════════════════════════════
echo  WALL-E AI - Instalador Completo v2.1
echo  Compatible con todas las dependencias
echo ════════════════════════════════════════
echo.

REM -------------------------
REM 0) Comprobar Python
REM -------------------------
echo [1/15] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [X] Python no encontrado en PATH.
    echo     Por favor instala Python 3.10+ y marca "Add to PATH".
    echo     Descarga: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python disponible
echo.

REM -------------------------
REM 1) Comprobar estructura del proyecto
REM -------------------------
echo [2/15] Verificando estructura del proyecto...
if not exist "backend\main.py" (
    echo [X] No se detecto backend\main.py.
    echo     Asegurate de ejecutar este script desde la raiz del proyecto.
    pause
    exit /b 1
)
if not exist "backend\config.py" (
    echo [X] No se detecto backend\config.py.
    pause
    exit /b 1
)
echo [OK] Estructura base detectada
echo.

REM -------------------------
REM 2) Limpiar venv previo (opcional)
REM -------------------------
echo [3/15] Verificando entorno virtual anterior...
if exist "venv" (
    echo [*] Se encontro venv. Eliminando entorno virtual anterior...
    rmdir /s /q venv 2>nul
    timeout /t 1 /nobreak >nul
    if exist "venv" (
        echo [!] No se pudo eliminar venv automaticamente.
        echo     Cierra terminales que lo usen o elimina la carpeta venv manualmente.
        pause
        exit /b 1
    )
)
echo [OK] Entorno virtual limpio
echo.

REM -------------------------
REM 3) Crear entorno virtual
REM -------------------------
echo [4/15] Creando entorno virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo [X] Error creando entorno virtual.
    echo     Asegurate de tener permisos y Python instalado correctamente.
    pause
    exit /b 1
)
if not exist "venv\Scripts\activate.bat" (
    echo [X] Entorno creado pero no se encontro activate.bat
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado
echo.

REM -------------------------
REM 4) Activar entorno virtual
REM -------------------------
echo [5/15] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [X] Error al activar el entorno virtual.
    pause
    exit /b 1
)
echo [OK] Entorno activado
echo.

REM -------------------------
REM 5) Actualizar pip y herramientas basicas
REM -------------------------
echo [6/15] Actualizando pip, setuptools y wheel...
python -m pip install --upgrade pip setuptools wheel --quiet
if %errorlevel% neq 0 (
    echo [!] Advertencia: no se pudo actualizar pip. Continuando...
) else (
    echo [OK] pip actualizado
)
echo.

REM -------------------------
REM 6) Instalacion de dependencias CORE
REM -------------------------
echo [7/15] Instalando dependencias CORE (FastAPI, Uvicorn, etc)...
pip install --quiet fastapi==0.115.0 uvicorn[standard]==0.31.0 python-multipart==0.0.12
if %errorlevel% neq 0 goto install_error
pip install --quiet pydantic==2.9.2 pydantic-settings==2.5.2 python-dotenv==1.0.1
if %errorlevel% neq 0 goto install_error
pip install --quiet tinyllama
if %errorlevel% neq 0 goto install_error
echo [OK] Dependencias CORE instaladas
echo.

REM -------------------------
REM 7) Instalacion de dependencias HTTP/Web
REM -------------------------
echo [8/15] Instalando herramientas HTTP y Web Scraping...
pip install --quiet requests==2.32.3 httpx==0.28.1 certifi
if %errorlevel% neq 0 goto install_error
pip install --quiet beautifulsoup4==4.12.3 lxml html5lib
if %errorlevel% neq 0 goto install_error
echo [OK] Herramientas HTTP/Web instaladas
echo.

REM -------------------------
REM 8) Instalacion de NumPy y SciPy
REM -------------------------
echo [9/15] Instalando NumPy y SciPy...
pip install --quiet numpy==1.26.4 scipy scikit-learn
if %errorlevel% neq 0 goto install_error
echo [OK] NumPy y SciPy instalados
echo.

REM -------------------------
REM 9) Instalacion de ChromaDB 0.4.24 (CRITICO)
REM -------------------------
echo [10/15] Instalando ChromaDB 0.4.24 (version especifica)...
echo [*] Esto puede tomar varios minutos...
pip install --quiet chromadb==0.4.24 --no-cache-dir
if %errorlevel% neq 0 (
    echo [!] ChromaDB instalacion directa fallo. Intentando con dependencias...
    pip install --quiet hnswlib chroma-hnswlib==0.7.3
    pip install --quiet chromadb==0.4.24 --no-cache-dir
    if %errorlevel% neq 0 goto install_error
)
echo [OK] ChromaDB 0.4.24 instalado
echo.

REM -------------------------
REM 10) Instalacion de Sentence-Transformers
REM -------------------------
echo [11/15] Instalando Sentence-Transformers...
pip install --quiet sentence-transformers==3.1.0
if %errorlevel% neq 0 goto install_error
echo [OK] Sentence-Transformers instalado
echo.

REM -------------------------
REM 11) Instalacion de LangChain 0.2.16 (CRITICO)
REM -------------------------
echo [12/15] Instalando LangChain 0.2.16 (version especifica)...
pip install --quiet langchain==0.2.16 langchain-core==0.2.38 langchain-community==0.2.16
if %errorlevel% neq 0 goto install_error
pip install --quiet langchain-ollama==0.1.3
if %errorlevel% neq 0 goto install_error
echo [OK] LangChain instalado
echo.

REM -------------------------
REM 12) Instalacion de SQLAlchemy y aiosqlite
REM -------------------------
echo [13/15] Instalando SQLAlchemy y base de datos...
pip install --quiet sqlalchemy==2.0.35 aiosqlite==0.20.0 greenlet==3.1.1
if %errorlevel% neq 0 goto install_error
echo [OK] SQLAlchemy instalado
echo.

REM -------------------------
REM 13) Instalacion de dependencias OPCIONALES (STT/TTS)
REM -------------------------
echo [14/15] Instalando dependencias OPCIONALES (STT/TTS)...
echo [*] Si falla, la app funcionara sin funcionalidad de voz
pip install --quiet faster-whisper 2>nul
if %errorlevel% equ 0 (
    echo [OK] Faster-Whisper instalado
) else (
    echo [!] Faster-Whisper no disponible - funcionalidad STT desactivada
)

pip install --quiet TTS 2>nul
if %errorlevel% equ 0 (
    echo [OK] Coqui TTS instalado
) else (
    echo [!] Coqui TTS no disponible - funcionalidad TTS desactivada
)
echo.

REM -------------------------
REM 14) Verificacion de imports criticos
REM -------------------------
echo [15/15] Verificando imports criticos...
python -c "import fastapi, uvicorn, chromadb, langchain, sentence_transformers, sqlalchemy" 2>nul
if %errorlevel% neq 0 (
    echo [!] Uno o varios imports criticos fallaron.
    echo     Revisa la salida en la terminal o ejecuta:
    echo     call venv\Scripts\activate.bat
    echo     python -c "import fastapi, uvicorn, chromadb, langchain"
    pause
    exit /b 1
)
echo [OK] Imports basicos verificados
echo.

REM Verificar versiones instaladas
python -c "import chromadb; print('ChromaDB:', chromadb.__version__)" 2>nul
python -c "import langchain; print('LangChain:', langchain.__version__)" 2>nul
echo.

REM -------------------------
REM 15) Crear estructura de carpetas necesarias
REM -------------------------
echo [*] Creando estructura de carpetas...
if not exist "chromadb_data" mkdir chromadb_data
if not exist "audio_output" mkdir audio_output
if not exist "logs" mkdir logs
if not exist "frontend" mkdir frontend

REM Crear __init__.py files
if not exist "backend\__init__.py" echo # Backend package > backend\__init__.py
if not exist "backend\models" mkdir backend\models
if not exist "backend\models\__init__.py" echo # Models package > backend\models\__init__.py
if not exist "backend\services" mkdir backend\services
if not exist "backend\services\__init__.py" echo # Services package > backend\services\__init__.py
if not exist "backend\agents" mkdir backend\agents
if not exist "backend\agents\__init__.py" echo # Agents package > backend\agents\__init__.py

echo [OK] Estructura creada/verificada
echo.

REM -------------------------
REM 16) Crear archivo .env si no existe
REM -------------------------
if not exist ".env" (
    echo OLLAMA_BASE_URL=http://localhost:11434 > .env
    echo OLLAMA_MODEL=gemma:2b >> .env
    echo WHISPER_MODEL=base >> .env
    echo TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2 >> .env
    echo DATABASE_URL=sqlite+aiosqlite:///./walle.db >> .env
    echo CHROMADB_PATH=./chromadb_data >> .env
    echo MAX_SEARCH_RESULTS=3 >> .env
    echo MAX_MEMORY_MESSAGES=20 >> .env
    echo SESSION_TIMEOUT_HOURS=24 >> .env
    echo [*] .env de ejemplo creado con modelo gemma:2b
) else (
    echo [*] .env ya existe (no modificado)
)
echo.

REM -------------------------
REM MENSAJES FINALES
REM -------------------------
echo.
echo ════════════════════════════════════════
echo  INSTALACION COMPLETADA EXITOSAMENTE
echo ════════════════════════════════════════
echo.
echo  Versiones instaladas:
python -c "import chromadb; print('  - ChromaDB:', chromadb.__version__)" 2>nul
python -c "import langchain; print('  - LangChain:', langchain.__version__)" 2>nul
python -c "import sentence_transformers; print('  - Sentence-Transformers: OK')" 2>nul
echo.
echo  Siguientes pasos:
echo   1) Asegurate de que Ollama este corriendo: ollama serve
echo   2) Descarga el modelo: ollama pull gemma:2b
echo   3) Ejecuta: start.bat
echo.
echo ════════════════════════════════════════
echo.
pause
exit /b 0

:install_error
echo.
echo ════════════════════════════════════════
echo  ERROR EN LA INSTALACION DE DEPENDENCIAS
echo ════════════════════════════════════════
echo  Recomendaciones:
echo   - Verifica conexion a internet
echo   - Ejecuta como administrador si hay errores de permisos
echo   - Instala Visual C++ Build Tools (para compilacion de ruedas)
echo   - Revisa el error especifico arriba
echo.
echo  Para reinstalar:
echo   1. Elimina la carpeta venv manualmente
echo   2. Ejecuta install.bat nuevamente
echo.
pause
exit /b 1