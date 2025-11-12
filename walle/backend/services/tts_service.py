"""
Text-to-Speech service using Coqui TTS
"""
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

# Intentar importar TTS, si falla, desactivar funcionalidad
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ TTS no está instalado. Funcionalidad de voz desactivada.")
    TTS_AVAILABLE = False

from backend.config import settings


class TTSService:
    def __init__(self):
        self.model = None
        self.is_loaded = False
        self.output_dir = "./audio_output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_model(self):
        """Load TTS model on startup"""
        if not TTS_AVAILABLE:
            logger.warning("⚠️ TTS no disponible - funcionalidad de voz desactivada")
            return
        
        try:
            logger.info(f"Loading TTS model: {settings.TTS_MODEL}")
            self.model = TTS(settings.TTS_MODEL, progress_bar=False)
            self.is_loaded = True
            logger.info("✅ TTS model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load TTS: {e}")
            logger.warning("⚠️ Continuando sin funcionalidad de voz")
            self.is_loaded = False
    
    async def synthesize(self, text: str, language: str = "es", session_id: str = "default") -> str:
        """
        Convert text to speech
        
        Args:
            text: Text to synthesize
            language: Language code
            session_id: Session identifier for filename
        
        Returns:
            Path to generated audio file or None if TTS not available
        """
        if not TTS_AVAILABLE or not self.is_loaded:
            logger.warning("⚠️ TTS no disponible - retornando None")
            return None
        
        try:
            # Generate unique filename
            filename = f"{session_id}_{hash(text) % 10000}.wav"
            output_path = os.path.join(self.output_dir, filename)
            
            # Synthesize
            self.model.tts_to_file(
                text=text[:500],  # Limit text length
                file_path=output_path,
                language=language
            )
            
            logger.info(f"🔊 Generated audio: {filename}")
            return output_path
        
        except Exception as e:
            logger.error(f"❌ TTS synthesis failed: {e}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove old audio files"""
        import time
        try:
            now = time.time()
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath):
                    age = now - os.path.getmtime(filepath)
                    if age > max_age_hours * 3600:
                        os.remove(filepath)
                        logger.info(f"🗑️ Cleaned up old audio: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")


# Singleton instance
tts_service = TTSService()