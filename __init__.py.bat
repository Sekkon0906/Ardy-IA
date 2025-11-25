@echo off
chcp 65001 >nul
cls

echo ════════════════════════════════════════
echo  Creando archivos __init__.py faltantes
echo ════════════════════════════════════════
echo.

REM Verificar que estamos en el directorio correcto
if not exist "backend" (
    echo [X] No se encuentra la carpeta backend
    echo     Este script debe ejecutarse desde la raiz del proyecto
    pause
    exit /b 1
)

REM Crear __init__.py en backend/
if not exist "backend\__init__.py" (
    echo # Backend package > backend\__init__.py
    echo [OK] Creado: backend\__init__.py
) else (
    echo [*] Ya existe: backend\__init__.py
)

REM Crear __init__.py en backend/models/
if not exist "backend\models\__init__.py" (
    echo # Models package > backend\models\__init__.py
    echo [OK] Creado: backend\models\__init__.py
) else (
    echo [*] Ya existe: backend\models\__init__.py
)

REM Crear __init__.py en backend/services/
if not exist "backend\services\__init__.py" (
    echo # Services package > backend\services\__init__.py
    echo [OK] Creado: backend\services\__init__.py
) else (
    echo [*] Ya existe: backend\services\__init__.py
)

REM Crear __init__.py en backend/agents/
if not exist "backend\agents\__init__.py" (
    echo # Agents package > backend\agents\__init__.py
    echo [OK] Creado: backend\agents\__init__.py
) else (
    echo [*] Ya existe: backend\agents\__init__.py
)

echo.
echo ════════════════════════════════════════
echo  Completado
echo ════════════════════════════════════════
echo.
echo Estructura verificada:
echo   backend\__init__.py
echo   backend\models\__init__.py
echo   backend\services\__init__.py
echo   backend\agents\__init__.py
echo.
echo Ahora puedes ejecutar: start.bat
echo.
pause