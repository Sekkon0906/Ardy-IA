"""
Speech-to-Text service using Faster Whisper
"""
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

# Intentar importar Whisper
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Faster Whisper no está instalado. Funcionalidad de voz desactivada.")
    WHISPER_AVAILABLE = False

from backend.config import settings


class STTService:
    def __init__(self):
        self.model = None
        self.is_loaded = False
    
    def load_model(self):
        """Load Whisper model on startup"""
        if not WHISPER_AVAILABLE:
            logger.warning("⚠️ Whisper no disponible - funcionalidad de transcripción desactivada")
            return
        
        try:
            logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
            self.model = WhisperModel(
                settings.WHISPER_MODEL,
                device="cpu",
                compute_type="int8"
            )
            self.is_loaded = True
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper: {e}")
            logger.warning("⚠️ Continuando sin funcionalidad de transcripción")
            self.is_loaded = False
    
    async def transcribe(self, audio_file: bytes, language: str = None) -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_file: Audio file bytes
            language: Language code (optional, auto-detect if None)
        
        Returns:
            Transcribed text or error message
        """
        if not WHISPER_AVAILABLE or not self.is_loaded:
            raise Exception("Servicio de transcripción no disponible")
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_file)
                tmp_path = tmp_file.name
            
            # Transcribe
            segments, info = self.model.transcribe(
                tmp_path,
                language=language,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine all segments
            transcription = " ".join([segment.text for segment in segments])
            
            # Cleanup
            os.unlink(tmp_path)
            
            logger.info(f"🎤 Transcribed ({info.language}): {transcription[:50]}...")
            return transcription.strip()
        
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise Exception(f"Error de transcripción: {str(e)}")


# Singleton instance
stt_service = STTService()