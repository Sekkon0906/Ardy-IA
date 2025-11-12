"""
WALL-E AI - Main FastAPI Application
Complete language learning assistant with voice input/output
COMPATIBLE with ChromaDB 0.4.24, LangChain 0.2.16
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    logger.info("🚀 Starting WALL-E AI...")
    
    # Verificar versiones (SIN CrewAI)
    try:
        import chromadb
        import langchain
        logger.info(f"📦 ChromaDB: {chromadb.__version__}")
        logger.info(f"📦 LangChain: {langchain.__version__}")
    except Exception as e:
        logger.warning(f"⚠️ No se pudieron verificar versiones: {e}")
    
    # Load models (optional, pueden no estar instalados)
    try:
        stt_service.load_model()
    except Exception as e:
        logger.warning(f"⚠️ STT service no disponible: {e}")
    
    try:
        tts_service.load_model()
    except Exception as e:
        logger.warning(f"⚠️ TTS service no disponible: {e}")
    
    # Test ChromaDB connection
    try:
        if rag_service.test_connection():
            logger.info("✅ ChromaDB conectado correctamente")
        else:
            logger.warning("⚠️ ChromaDB connection test failed")
    except Exception as e:
        logger.error(f"❌ ChromaDB error: {e}")
    
    # Cleanup old data
    try:
        memory_service.cleanup_old_sessions()
        tts_service.cleanup_old_files()
    except Exception as e:
        logger.warning(f"⚠️ Cleanup warning: {e}")
    
    logger.info("✅ WALL-E AI ready!")
    
    yield
    
    logger.info("👋 Shutting down WALL-E AI...")


# Initialize FastAPI
app = FastAPI(
    title="WALL-E AI",
    description="Multilingual Language Learning Assistant with Voice",
    version="2.1.0",
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

# Serve static audio files (crear directorio si no existe)
os.makedirs("audio_output", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio_output"), name="audio")


@app.get("/", response_class=FileResponse)
async def root():
    """Serve frontend"""
    # Verificar si existe index.html
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    else:
        return {"message": "WALL-E AI API is running", "version": "2.1.0", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Test Ollama connection
    ollama_ok = False
    try:
        import httpx
        response = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        ollama_ok = response.status_code == 200
    except:
        pass
    
    return HealthResponse(
        status="healthy",
        ollama_connected=ollama_ok,
        whisper_loaded=stt_service.is_loaded,
        tts_loaded=tts_service.is_loaded
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Text-based chat endpoint
    
    Processes user's text message and returns AI response
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or memory_service.generate_session_id()
        
        logger.info(f"💬 Chat request: {request.query[:50]}...")
        
        # Save user message
        memory_service.add_message(session_id, "user", request.query, request.lang)
        
        # Get conversation context
        memory_context = memory_service.get_context_string(session_id, max_messages=10)
        
        # RAG search if enabled
        rag_context = ""
        if request.use_rag:
            try:
                rag_context = rag_service.rag_search(request.query, request.lang)
            except Exception as e:
                logger.error(f"❌ RAG search failed: {e}")
                rag_context = ""
        
        # Run teaching crew
        response_text = run_teaching_crew(
            query=request.query,
            language=request.lang,
            memory_context=memory_context,
            research_context=rag_context
        )
        
        # Save assistant response
        memory_service.add_message(session_id, "assistant", response_text, request.lang)
        
        # Get conversation history
        history = memory_service.get_conversation_history(session_id, limit=10)
        
        return ChatResponse(
            answer=response_text,
            session_id=session_id,
            memory=history,
            rag_used=request.use_rag and bool(rag_context)
        )
    
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        logger.exception("Error details:")
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")


@app.post("/voice", response_model=AudioResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    lang: str = "es",
    session_id: str = None,
    use_rag: bool = True
):
    """
    Voice-based chat endpoint
    
    Accepts audio file, transcribes it, processes with AI, and returns text + audio response
    """
    try:
        # Verificar que STT esté disponible
        if not stt_service.is_loaded:
            raise HTTPException(
                status_code=503, 
                detail="Servicio de transcripción no disponible. Instala faster-whisper."
            )
        
        session_id = session_id or memory_service.generate_session_id()
        
        logger.info(f"🎤 Voice request from session: {session_id}")
        
        # Read audio file
        audio_bytes = await audio.read()
        
        # Transcribe audio
        transcription = await stt_service.transcribe(audio_bytes, language=lang)
        
        if not transcription:
            raise HTTPException(status_code=400, detail="No speech detected in audio")
        
        logger.info(f"📝 Transcribed: {transcription}")
        
        # Process like text chat
        memory_service.add_message(session_id, "user", transcription, lang)
        memory_context = memory_service.get_context_string(session_id, max_messages=10)
        
        rag_context = ""
        if use_rag:
            try:
                rag_context = rag_service.rag_search(transcription, lang)
            except Exception as e:
                logger.error(f"❌ RAG search failed: {e}")
        
        response_text = run_teaching_crew(
            query=transcription,
            language=lang,
            memory_context=memory_context,
            research_context=rag_context
        )
        
        memory_service.add_message(session_id, "assistant", response_text, lang)
        
        # Generate audio response (if TTS available)
        audio_url = None
        if tts_service.is_loaded:
            try:
                audio_path = await tts_service.synthesize(response_text, lang, session_id)
                audio_url = f"/audio/{audio_path.split('/')[-1]}" if audio_path else None
            except Exception as e:
                logger.warning(f"⚠️ TTS failed: {e}")
        
        return AudioResponse(
            transcription=transcription,
            answer=response_text,
            session_id=session_id,
            audio_url=audio_url
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Voice chat error: {e}")
        logger.exception("Error details:")
        raise HTTPException(status_code=500, detail=f"Error procesando audio: {str(e)}")


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a session"""
    try:
        # TODO: Implementar método delete en memory_service
        return {"message": "Session cleared", "session_id": session_id}
    except Exception as e:
        logger.error(f"❌ Clear session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# FIX: Protección para Windows multiprocessing
if __name__ == "__main__":
    import uvicorn
    
    # FIX: Configuración optimizada para Windows
    uvicorn.run(
        "backend.main:app",  # String path para evitar problemas de reload
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Desactivar reload en producción
        log_level="info"
    )