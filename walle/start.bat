@echo off
chcp 65001 >nul
cls

echo ════════════════════════════════════════
echo  WALL-E AI - Language Tutor v2.1
echo  Iniciando servidor...
echo ════════════════════════════════════════
echo.

REM ════════════════════════════════════════
REM PASO 1: Verificar estructura del proyecto
REM ════════════════════════════════════════
echo [1/8] Verificando estructura del proyecto...
if not exist "backend\main.py" (
    echo [X] ERROR: No se encuentra backend\main.py
    echo.
    echo     Este script debe ejecutarse desde la raiz del proyecto
    echo.
    pause
    exit /b 1
)
if not exist "backend\config.py" (
    echo [X] ERROR: No se encuentra backend\config.py
    pause
    exit /b 1
)
echo [OK] Estructura del proyecto verificada
echo.

REM ════════════════════════════════════════
REM PASO 2: Verificar Ollama (MEJORADO)
REM ════════════════════════════════════════
echo [2/8] Verificando Ollama...

REM Metodo 1: Verificar proceso
tasklist | findstr /I "ollama" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama esta corriendo ^(proceso detectado^)
    goto ollama_ok
)

REM Metodo 2: Verificar puerto 11434
netstat -ano | findstr :11434 | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama esta corriendo ^(puerto 11434 activo^)
    goto ollama_ok
)

REM Metodo 3: Intentar con PowerShell (Windows 10+)
powershell -Command "try { $null = Invoke-WebRequest -Uri 'http://localhost:11434' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama esta corriendo ^(verificado via HTTP^)
    goto ollama_ok
)

REM Si ninguno funciona, mostrar error
echo [X] Ollama NO esta corriendo
echo.
echo     SOLUCION - Opciones disponibles:
echo.
echo     [A] Abrir nueva ventana y ejecutar: ollama serve
echo     [B] Si ya esta corriendo, presiona para continuar
echo     [C] Salir y verificar manualmente
echo.
choice /C ABC /N /M "Selecciona [A/B/C]: "
if %errorlevel% equ 3 (
    echo [*] Saliendo...
    pause
    exit /b 1
)
if %errorlevel% equ 2 (
    echo [!] Continuando sin verificacion...
    goto ollama_ok
)
if %errorlevel% equ 1 (
    echo.
    echo [*] INSTRUCCIONES:
    echo     1. Abre OTRA ventana de CMD/PowerShell
    echo     2. Ejecuta: ollama serve
    echo     3. Vuelve a esta ventana y presiona Enter
    echo.
    pause
    exit /b 1
)

:ollama_ok
echo.

REM ════════════════════════════════════════
REM PASO 3: Verificar modelo gemma:2b
REM ════════════════════════════════════════
echo [3/9] Verificando modelo gemma:2b...
ollama list 2>nul | findstr /I "gemma:2b" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Modelo gemma:2b NO encontrado
    echo.
    echo     Este modelo es REQUERIDO por la aplicacion
    echo.
    echo     OPCIONES:
    echo     [A] Descargar ahora gemma:2b ^(~1.6GB, 3-5 minutos^)
    echo     [B] Salir y descargar manualmente: ollama pull gemma:2b
    echo.
    choice /C AB /N /M "Que deseas hacer [A/B]: "
    if %errorlevel% equ 2 (
        echo.
        echo [*] Ejecuta manualmente: ollama pull gemma:2b
        echo     Luego vuelve a ejecutar start.bat
        pause
        exit /b 1
    )
    echo.
    echo [*] Descargando gemma:2b...
    echo [*] Esto puede tomar varios minutos...
    ollama pull gemma:2b
    if %errorlevel% neq 0 (
        echo [X] Error al descargar modelo
        echo.
        echo     Verifica:
        echo     - Conexion a internet
        echo     - Espacio en disco (minimo 2GB libres)
        echo.
        pause
        exit /b 1
    )
    echo [OK] Modelo gemma:2b descargado
) else (
    echo [OK] Modelo gemma:2b disponible
)
echo.

REM ════════════════════════════════════════
REM PASO 4: Verificar entorno virtual
REM ════════════════════════════════════════
echo [4/8] Verificando entorno virtual...
if not exist "venv\Scripts\activate.bat" (
    echo [X] Entorno virtual NO encontrado
    echo.
    echo     SOLUCION: Ejecuta install.bat primero
    echo.
    pause
    exit /b 1
)
echo [OK] Entorno virtual encontrado
echo.

REM ════════════════════════════════════════
REM PASO 5: Verificar y limpiar ChromaDB si es necesario
REM ════════════════════════════════════════
echo [5/8] Verificando base de datos ChromaDB...

REM Verificar si existe chroma.sqlite3 con problemas
if exist "chromadb_data\chroma.sqlite3" (
    echo [*] Base de datos ChromaDB encontrada, verificando integridad...
    
    REM Intentar verificar si la BD esta corrupta
    call venv\Scripts\activate.bat >nul 2>&1
    python -c "import sqlite3; conn = sqlite3.connect('chromadb_data/chroma.sqlite3'); cur = conn.cursor(); cur.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"collections\"'); tables = cur.fetchall(); cur.execute('PRAGMA table_info(collections)'); cols = [row[1] for row in cur.fetchall()]; conn.close(); exit(0 if 'topic' in cols or len(tables) == 0 else 1)" 2>nul
    
    if %errorlevel% neq 0 (
        echo [!] Base de datos ChromaDB corrupta detectada
        echo     Esto sucede por incompatibilidad de versiones
        echo.
        echo     ¿Deseas limpiar la base de datos? ^(Se perderan datos vectoriales^)
        echo     ^(El historial de conversaciones NO se vera afectado^)
        echo.
        choice /C SN /N /M "Presiona S para Si, N para No: "
        if %errorlevel% equ 1 (
            echo.
            echo [*] Limpiando base de datos ChromaDB...
            rmdir /s /q chromadb_data 2>nul
            timeout /t 1 /nobreak >nul
            if exist "chromadb_data" (
                echo [X] No se pudo limpiar automaticamente
                echo.
                echo     SOLUCION MANUAL:
                echo     1. Cierra esta ventana
                echo     2. Elimina manualmente la carpeta: chromadb_data
                echo     3. Ejecuta start.bat nuevamente
                echo.
                echo     O ejecuta: cleanup_chromadb.bat
                echo.
                pause
                exit /b 1
            )
            mkdir chromadb_data
            echo [OK] Base de datos limpiada, se recreara automaticamente
        ) else (
            echo.
            echo [X] No se puede continuar con base de datos corrupta
            echo.
            echo     Ejecuta: cleanup_chromadb.bat
            echo     O elimina manualmente la carpeta: chromadb_data
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo [OK] Base de datos ChromaDB integra
    )
) else (
    echo [*] Base de datos ChromaDB no existe, se creara automaticamente
)

REM Crear directorios necesarios
if not exist "chromadb_data" mkdir chromadb_data
if not exist "audio_output" mkdir audio_output
if not exist "logs" mkdir logs
if not exist "frontend" mkdir frontend

REM ════════════════════════════════════════
REM PASO 6: Verificar __init__.py files
REM ════════════════════════════════════════
echo [6/8] Verificando modulos Python...
if not exist "backend\__init__.py" (
    echo # Backend package > backend\__init__.py
)
if not exist "backend\models\__init__.py" (
    if not exist "backend\models" mkdir backend\models
    echo # Models package > backend\models\__init__.py
)
if not exist "backend\services\__init__.py" (
    if not exist "backend\services" mkdir backend\services
    echo # Services package > backend\services\__init__.py
)
if not exist "backend\agents\__init__.py" (
    if not exist "backend\agents" mkdir backend\agents
    echo # Agents package > backend\agents\__init__.py
)

echo [OK] Modulos Python verificados
echo.

REM ════════════════════════════════════════
REM PASO 7: Activar entorno virtual
REM ════════════════════════════════════════
echo [7/8] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [X] Error al activar entorno virtual
    echo.
    echo     SOLUCION: Ejecuta install.bat nuevamente
    echo.
    pause
    exit /b 1
)
echo [OK] Entorno activado
echo.

REM ════════════════════════════════════════
REM PASO 8: Verificar modulos criticos
REM ════════════════════════════════════════
echo [8/8] Verificando modulos criticos...

python -c "import fastapi, uvicorn" 2>nul
if %errorlevel% neq 0 (
    echo [X] Faltan modulos criticos ^(FastAPI/Uvicorn^)
    echo.
    echo     SOLUCION: Ejecuta install.bat nuevamente
    echo.
    pause
    exit /b 1
)

python -c "import chromadb" 2>nul
if %errorlevel% neq 0 (
    echo [X] ChromaDB no esta instalado
    echo.
    echo     SOLUCION: Ejecuta install.bat nuevamente
    echo.
    pause
    exit /b 1
)

python -c "import langchain" 2>nul
if %errorlevel% neq 0 (
    echo [X] LangChain no esta instalado
    echo.
    echo     SOLUCION: Ejecuta install.bat nuevamente
    echo.
    pause
    exit /b 1
)

python -c "import sentence_transformers" 2>nul
if %errorlevel% neq 0 (
    echo [X] Sentence-Transformers no esta instalado
    echo.
    echo     SOLUCION: Ejecuta install.bat nuevamente
    echo.
    pause
    exit /b 1
)

python -c "import sqlalchemy" 2>nul
if %errorlevel% neq 0 (
    echo [X] SQLAlchemy no esta instalado
    echo.
    echo     SOLUCION: Ejecuta install.bat nuevamente
    echo.
    pause
    exit /b 1
)

echo [OK] Todos los modulos criticos disponibles
echo.

REM Mostrar versiones instaladas
echo [*] Versiones detectadas:
python -c "import chromadb; print('    ChromaDB:', chromadb.__version__)" 2>nul
python -c "import langchain; print('    LangChain:', langchain.__version__)" 2>nul
echo.

REM ════════════════════════════════════════
REM PASO 9: Verificar archivo .env
REM ════════════════════════════════════════
echo [*] Verificando configuracion (.env)...
if not exist ".env" (
    echo [!] Archivo .env no encontrado. Creando con valores por defecto...
    echo OLLAMA_BASE_URL=http://localhost:11434 > .env
    echo OLLAMA_MODEL=gemma:2b >> .env
    echo WHISPER_MODEL=base >> .env
    echo DATABASE_URL=sqlite+aiosqlite:///./walle.db >> .env
    echo CHROMADB_PATH=./chromadb_data >> .env
    echo MAX_SEARCH_RESULTS=3 >> .env
    echo [OK] .env creado
) else (
    echo [OK] .env encontrado
)
echo.

REM ════════════════════════════════════════
REM MOSTRAR INFORMACION
REM ════════════════════════════════════════
echo ════════════════════════════════════════
echo  CONFIGURACION DEL SERVIDOR
echo ════════════════════════════════════════
echo  Ollama:       http://localhost:11434
echo  Modelo:       gemma:2b
echo  Servidor:     http://localhost:8000
echo  API Docs:     http://localhost:8000/docs
echo  ChromaDB:     ./chromadb_data
echo  Database:     ./walle.db
echo ════════════════════════════════════════
echo.
echo  [*] Iniciando servidor WALL-E AI...
echo  [*] Presiona Ctrl+C para detener
echo.
echo  Abre tu navegador en: http://localhost:8000
echo  O usa la API en: http://localhost:8000/docs
echo.
echo ════════════════════════════════════════
echo.

REM ════════════════════════════════════════
REM INICIAR SERVIDOR
REM ════════════════════════════════════════
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

REM ════════════════════════════════════════
REM SI LLEGAMOS AQUI, HUBO UN ERROR
REM ════════════════════════════════════════
if %errorlevel% neq 0 (
    echo.
    echo ════════════════════════════════════════
    echo  ERROR AL INICIAR SERVIDOR
    echo ════════════════════════════════════════
    echo.
    echo  Para ver el error detallado, ejecuta:
    echo.
    echo  call venv\Scripts\activate.bat
    echo  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
    echo.
    echo  O revisa los logs en ./logs/
    echo.
    echo ════════════════════════════════════════
)

echo.
pause