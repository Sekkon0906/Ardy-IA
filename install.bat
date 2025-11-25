@echo off
chcp 65001 >nul
cls

echo ════════════════════════════════════════
echo  WALL-E AI - Installateur GROQ v2.1
echo  LLM Gratuit + Rapide + Sans limite
echo ════════════════════════════════════════
echo.

REM Vérifier Python
echo [1/10] Vérification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python non trouvé
    echo     Installe Python 3.10+ depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python disponible
echo.

REM Vérifier structure
echo [2/10] Vérification de la structure...
if not exist "backend\main.py" (
    echo [X] backend\main.py introuvable
    pause
    exit /b 1
)
echo [OK] Structure OK
echo.

REM Nettoyer ancien venv
echo [3/10] Nettoyage de l'ancien environnement...
if exist "venv" (
    echo [*] Suppression de l'ancien venv...
    rmdir /s /q venv 2>nul
    timeout /t 1 /nobreak >nul
)
echo [OK] Environnement nettoyé
echo.

REM Créer venv
echo [4/10] Création de l'environnement virtuel...
python -m venv venv
if %errorlevel% neq 0 (
    echo [X] Erreur création venv
    pause
    exit /b 1
)
echo [OK] Venv créé
echo.

REM Activer venv
echo [5/10] Activation de l'environnement...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [X] Erreur activation venv
    pause
    exit /b 1
)
echo [OK] Venv activé
echo.

REM Mettre à jour pip
echo [6/10] Mise à jour de pip...
python -m pip install --upgrade pip setuptools wheel --quiet
echo [OK] Pip mis à jour
echo.

REM Installer dépendances CORE
echo [7/10] Installation des dépendances CORE...
pip install --quiet fastapi==0.115.0 uvicorn[standard]==0.31.0 python-multipart==0.0.12
pip install --quiet pydantic==2.9.2 pydantic-settings==2.5.2 python-dotenv==1.0.1
pip install --quiet requests==2.32.3 httpx==0.28.1 beautifulsoup4==4.12.3
echo [OK] Dépendances CORE installées
echo.

REM Installer GROQ
echo [8/10] Installation de Groq API (GRATUIT)...
pip install --quiet groq
if %errorlevel% neq 0 (
    echo [X] Erreur installation Groq
    goto install_error
)
echo [OK] Groq installé
echo.

REM Installer ML libraries
echo [9/10] Installation des bibliothèques ML...
pip install --quiet numpy==1.26.4 scipy scikit-learn
pip install --quiet sentence-transformers==3.1.0
pip install --quiet chromadb==0.4.24
pip install --quiet sqlalchemy==2.0.35 aiosqlite==0.20.0
echo [OK] Bibliothèques ML installées
echo.

REM Vérifier imports
echo [10/10] Vérification des imports...
python -c "import fastapi, uvicorn, groq, chromadb, sentence_transformers, sqlalchemy" 2>nul
if %errorlevel% neq 0 (
    echo [X] Erreur dans les imports
    pause
    exit /b 1
)
echo [OK] Tous les imports OK
echo.

REM Créer structure
echo [*] Création de la structure...
if not exist "chromadb_data" mkdir chromadb_data
if not exist "audio_output" mkdir audio_output
if not exist "logs" mkdir logs
if not exist "frontend" mkdir frontend

REM Créer __init__.py
if not exist "backend\__init__.py" echo # Backend package > backend\__init__.py
if not exist "backend\models" mkdir backend\models
if not exist "backend\models\__init__.py" echo # Models package > backend\models\__init__.py
if not exist "backend\services" mkdir backend\services
if not exist "backend\services\__init__.py" echo # Services package > backend\services\__init__.py
if not exist "backend\agents" mkdir backend\agents
if not exist "backend\agents\__init__.py" echo # Agents package > backend\agents\__init__.py
echo [OK] Structure créée
echo.

REM Créer .env
if not exist ".env" (
    echo # Clé API Groq (GRATUIT): https://console.groq.com/keys > .env
    echo GROQ_API_KEY= >> .env
    echo GROQ_MODEL=llama-3.1-70b-versatile >> .env
    echo MODEL_TEMPERATURE=0.8 >> .env
    echo MODEL_MAX_TOKENS=500 >> .env
    echo DATABASE_URL=sqlite+aiosqlite:///./walle.db >> .env
    echo CHROMADB_PATH=./chromadb_data >> .env
    echo MAX_SEARCH_RESULTS=3 >> .env
    echo [*] Fichier .env créé
)
echo.

REM Messages finaux
echo ════════════════════════════════════════
echo  INSTALLATION TERMINÉE ✅
echo ════════════════════════════════════════
echo.
echo  Prochaines étapes:
echo.
echo  1. Obtiens ta clé API Groq GRATUITE:
echo     https://console.groq.com/keys
echo.
echo  2. Copie la clé et modifie le fichier .env:
echo     GROQ_API_KEY=gsk_ta_cle_ici
echo.
echo  3. Lance l'application:
echo     start.bat
echo.
echo ════════════════════════════════════════
echo.
pause
exit /b 0

:install_error
echo.
echo ════════════════════════════════════════
echo  ERREUR D'INSTALLATION
echo ════════════════════════════════════════
echo.
echo  Vérifie:
echo  - Connexion Internet
echo  - Espace disque (minimum 1GB)
echo  - Permissions administrateur
echo.
pause
exit /b 1
