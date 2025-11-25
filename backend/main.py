"""
WALL-E AI - Main FastAPI Application
Complete language learning assistant with Groq API
VERSION GROQ (GRATUIT et RAPIDE)
"""
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from backend.config import settings
from backend.models.schemas import (
    ChatRequest, ChatResponse, AudioResponse, HealthResponse
)
from backend.services.stt_service import stt_service
from backend.services.tts_service import tts_service
from backend.services.memory_service import memory_service
from backend.services.rag_service import rag_service
from backend.agents.language_tutor import run_teaching_crew

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Événements de cycle de vie"""
    logger.info("🚀 Démarrage de WALL-E AI avec Groq...")
    
    # Vérifier les versions
    try:
        import chromadb
        import groq
        logger.info(f"📦 ChromaDB: {chromadb.__version__}")
        logger.info(f"📦 Groq: {groq.__version__}")
    except Exception as e:
        logger.warning(f"⚠️ Vérification des versions échouée: {e}")
    
    # Charger les modèles optionnels
    try:
        stt_service.load_model()
    except Exception as e:
        logger.warning(f"⚠️ STT non disponible: {e}")
    
    try:
        tts_service.load_model()
    except Exception as e:
        logger.warning(f"⚠️ TTS non disponible: {e}")
    
    # Test connexion ChromaDB
    try:
        if rag_service.test_connection():
            logger.info("✅ ChromaDB connecté")
        else:
            logger.warning("⚠️ ChromaDB test échoué")
    except Exception as e:
        logger.error(f"❌ Erreur ChromaDB: {e}")
    
    # Nettoyage
    try:
        memory_service.cleanup_old_sessions()
        tts_service.cleanup_old_files()
    except Exception as e:
        logger.warning(f"⚠️ Avertissement nettoyage: {e}")
    
    # Vérifier la clé API Groq
    if not settings.GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY non configurée dans .env!")
        logger.error("   Obtiens une clé gratuite sur: https://console.groq.com/keys")
    else:
        logger.info(f"✅ Groq API configurée (modèle: {settings.GROQ_MODEL})")
    
    logger.info("✅ WALL-E AI prêt!")
    
    yield
    
    logger.info("👋 Arrêt de WALL-E AI...")


# Initialiser FastAPI
app = FastAPI(
    title="WALL-E AI",
    description="Assistant d'apprentissage multilingue avec Groq",
    version="2.1.0-groq",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir fichiers audio statiques
os.makedirs("audio_output", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio_output"), name="audio")


@app.get("/", response_class=FileResponse)
async def root():
    """Servir le frontend"""
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    else:
        return {
            "message": "WALL-E AI API en cours d'exécution",
            "version": "2.1.0-groq",
            "provider": "Groq (GRATUIT)",
            "docs": "/docs"
        }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de santé"""
    # Test connexion Groq
    groq_ok = bool(settings.GROQ_API_KEY)
    
    return HealthResponse(
        status="healthy" if groq_ok else "degraded",
        ollama_connected=groq_ok,  # Réutilise le champ pour Groq
        whisper_loaded=stt_service.is_loaded,
        tts_loaded=tts_service.is_loaded
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint de chat textuel
    
    Traite le message de l'utilisateur et retourne une réponse IA
    """
    try:
        # Vérifier la clé API
        if not settings.GROQ_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="Clé API Groq non configurée. Configure GROQ_API_KEY dans .env"
            )
        
        # Générer session ID si absent
        session_id = request.session_id or memory_service.generate_session_id()
        
        logger.info(f"💬 Requête chat: {request.query[:50]}...")
        
        # Sauvegarder message utilisateur
        memory_service.add_message(session_id, "user", request.query, request.lang)
        
        # Obtenir contexte de conversation
        memory_context = memory_service.get_context_string(session_id, max_messages=10)
        
        # Recherche RAG si activée
        rag_context = ""
        if request.use_rag:
            try:
                rag_context = rag_service.rag_search(request.query, request.lang)
            except Exception as e:
                logger.error(f"❌ Recherche RAG échouée: {e}")
                rag_context = ""
        
        # Exécuter le teaching crew avec Groq
        response_text = run_teaching_crew(
            query=request.query,
            language=request.lang,
            memory_context=memory_context,
            research_context=rag_context
        )
        
        # Sauvegarder réponse assistant
        memory_service.add_message(session_id, "assistant", response_text, request.lang)
        
        # Obtenir historique
        history = memory_service.get_conversation_history(session_id, limit=10)
        
        return ChatResponse(
            answer=response_text,
            session_id=session_id,
            memory=history,
            rag_used=request.use_rag and bool(rag_context)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur chat: {e}")
        logger.exception("Détails de l'erreur:")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du message: {str(e)}"
        )


@app.post("/voice", response_model=AudioResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    lang: str = "es",
    session_id: str = None,
    use_rag: bool = True
):
    """
    Endpoint de chat vocal
    
    Accepte un fichier audio, le transcrit, traite avec l'IA, et retourne texte + audio
    """
    try:
        # Vérifier que STT est disponible
        if not stt_service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Service de transcription non disponible. Installe faster-whisper."
            )
        
        session_id = session_id or memory_service.generate_session_id()
        
        logger.info(f"🎤 Requête vocale de la session: {session_id}")
        
        # Lire le fichier audio
        audio_bytes = await audio.read()
        
        # Transcrire l'audio
        transcription = await stt_service.transcribe(audio_bytes, language=lang)
        
        if not transcription:
            raise HTTPException(
                status_code=400,
                detail="Aucune parole détectée dans l'audio"
            )
        
        logger.info(f"📝 Transcrit: {transcription}")
        
        # Traiter comme chat textuel
        memory_service.add_message(session_id, "user", transcription, lang)
        memory_context = memory_service.get_context_string(session_id, max_messages=10)
        
        rag_context = ""
        if use_rag:
            try:
                rag_context = rag_service.rag_search(transcription, lang)
            except Exception as e:
                logger.error(f"❌ Recherche RAG échouée: {e}")
        
        response_text = run_teaching_crew(
            query=transcription,
            language=lang,
            memory_context=memory_context,
            research_context=rag_context
        )
        
        memory_service.add_message(session_id, "assistant", response_text, lang)
        
        # Générer réponse audio (si TTS disponible)
        audio_url = None
        if tts_service.is_loaded:
            try:
                audio_path = await tts_service.synthesize(response_text, lang, session_id)
                audio_url = f"/audio/{audio_path.split('/')[-1]}" if audio_path else None
            except Exception as e:
                logger.warning(f"⚠️ TTS échoué: {e}")
        
        return AudioResponse(
            transcription=transcription,
            answer=response_text,
            session_id=session_id,
            audio_url=audio_url
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur chat vocal: {e}")
        logger.exception("Détails de l'erreur:")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de l'audio: {str(e)}"
        )


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Effacer l'historique de conversation d'une session"""
    try:
        # TODO: Implémenter méthode delete dans memory_service
        return {"message": "Session effacée", "session_id": session_id}
    except Exception as e:
        logger.error(f"❌ Erreur effacement session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Protection pour Windows multiprocessing
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )
