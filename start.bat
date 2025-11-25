@echo off
chcp 65001 >nul
cls

echo ════════════════════════════════════════
echo  WALL-E AI - Language Tutor v2.1
echo  Powered by Groq (GRATUIT)
echo ════════════════════════════════════════
echo.

REM Vérifier structure
echo [1/6] Vérification de la structure...
if not exist "backend\main.py" (
    echo [X] backend\main.py introuvable
    pause
    exit /b 1
)
echo [OK] Structure OK
echo.

REM Vérifier entorno virtual
echo [2/6] Vérification de l'environnement virtuel...
if not exist "venv\Scripts\activate.bat" (
    echo [X] Environnement virtuel introuvable
    echo.
    echo     Lance d'abord: install.bat
    echo.
    pause
    exit /b 1
)
echo [OK] Environnement trouvé
echo.

REM Vérifier et nettoyer ChromaDB si nécessaire
echo [3/6] Vérification de ChromaDB...
if exist "chromadb_data\chroma.sqlite3" (
    echo [*] Base de données ChromaDB trouvée
    call venv\Scripts\activate.bat >nul 2>&1
    python -c "import sqlite3; conn = sqlite3.connect('chromadb_data/chroma.sqlite3'); cur = conn.cursor(); cur.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"collections\"'); tables = cur.fetchall(); cur.execute('PRAGMA table_info(collections)'); cols = [row[1] for row in cur.fetchall()]; conn.close(); exit(0 if 'topic' in cols or len(tables) == 0 else 1)" 2>nul
    
    if %errorlevel% neq 0 (
        echo [!] Base de données corrompue détectée
        echo.
        choice /C SN /N /M "Nettoyer la base de données? (S=Oui, N=Non): "
        if %errorlevel% equ 1 (
            rmdir /s /q chromadb_data 2>nul
            mkdir chromadb_data
            echo [OK] Base de données nettoyée
        ) else (
            echo [X] Impossible de continuer avec une BD corrompue
            pause
            exit /b 1
        )
    ) else (
        echo [OK] Base de données intègre
    )
)

REM Créer dossiers
if not exist "chromadb_data" mkdir chromadb_data
if not exist "audio_output" mkdir audio_output
if not exist "logs" mkdir logs
echo.

REM Vérifier __init__.py
echo [4/6] Vérification des modules Python...
if not exist "backend\__init__.py" echo # Backend package > backend\__init__.py
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
echo [OK] Modules OK
echo.

REM Activer venv
echo [5/6] Activation de l'environnement...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [X] Erreur activation
    pause
    exit /b 1
)
echo [OK] Environnement activé
echo.

REM Vérifier modules critiques
echo [6/6] Vérification des modules...
python -c "import fastapi, uvicorn, groq" 2>nul
if %errorlevel% neq 0 (
    echo [X] Modules manquants
    echo     Lance: install.bat
    pause
    exit /b 1
)
echo [OK] Tous les modules disponibles
echo.

REM Vérifier .env
if not exist ".env" (
    echo [!] Fichier .env introuvable
    echo.
    echo [*] Création d'un .env par défaut...
    echo GROQ_API_KEY= > .env
    echo GROQ_MODEL=llama-3.1-70b-versatile >> .env
    echo MODEL_TEMPERATURE=0.8 >> .env
    echo MODEL_MAX_TOKENS=500 >> .env
    echo DATABASE_URL=sqlite+aiosqlite:///./walle.db >> .env
    echo CHROMADB_PATH=./chromadb_data >> .env
    echo.
    echo [!] IMPORTANT: Configure ta clé API dans .env
    echo     GROQ_API_KEY=gsk_ta_cle_ici
    echo.
    echo     Obtiens une clé gratuite sur:
    echo     https://console.groq.com/keys
    echo.
    pause
)

REM Vérifier que la clé API est configurée
findstr /C:"GROQ_API_KEY=gsk_" .env >nul 2>&1
if %errorlevel% neq 0 (
    findstr /C:"GROQ_API_KEY= " .env >nul 2>&1
    if %errorlevel% equ 0 (
        echo.
        echo ════════════════════════════════════════
        echo  ⚠️ CLÉ API GROQ NON CONFIGURÉE
        echo ════════════════════════════════════════
        echo.
        echo  1. Va sur: https://console.groq.com/keys
        echo  2. Crée un compte (GRATUIT)
        echo  3. Génère une clé API
        echo  4. Copie la clé dans le fichier .env:
        echo     GROQ_API_KEY=gsk_ta_cle_ici
        echo.
        echo  Appuie sur une touche pour continuer quand même
        echo  (le serveur démarrera mais les messages ne fonctionneront pas)
        echo.
        pause
    )
)

REM Afficher info
echo.
echo ════════════════════════════════════════
echo  CONFIGURATION
echo ════════════════════════════════════════
echo  Provider:     Groq (GRATUIT)
echo  Modèle:       llama-3.1-70b-versatile
echo  Serveur:      http://localhost:8000
echo  API Docs:     http://localhost:8000/docs
echo  Database:     ./walle.db
echo ════════════════════════════════════════
echo.
echo  [*] Démarrage du serveur...
echo  [*] Ouvre ton navigateur sur: http://localhost:8000
echo  [*] Ctrl+C pour arrêter
echo.
echo ════════════════════════════════════════
echo.

REM Démarrer serveur
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

REM Si erreur
if %errorlevel% neq 0 (
    echo.
    echo ════════════════════════════════════════
    echo  ERREUR AU DÉMARRAGE
    echo ════════════════════════════════════════
    echo.
    echo  Pour voir l'erreur détaillée:
    echo  call venv\Scripts\activate.bat
    echo  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
    echo.
    pause
)
