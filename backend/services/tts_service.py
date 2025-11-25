"""
Text-to-Speech service (Coqui TTS)
"""
import logging

logger = logging.getLogger(__name__)

# Intentar importar TTS
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except Exception as e:
    logger.error(f"TTS no disponible: {e}")
    TTS_AVAILABLE = False

from backend.config import settings


class TTSService:
    def __init__(self):
        self.model = None
        self.is_loaded = False

    def load_model(self):
        if not TTS_AVAILABLE:
            logger.warning("⚠️ TTS no disponible – continuando sin audio")
            return

        try:
            logger.info(f"🔊 Loading TTS model: {settings.TTS_MODEL}")

            # Carga del modelo correcto
            self.model = TTS(model_name=settings.TTS_MODEL, progress_bar=False, gpu=False)

            self.is_loaded = True
            logger.info("✅ TTS cargado correctamente")

        except Exception as e:
            logger.error(f"❌ Error al cargar TTS: {e}")
            self.is_loaded = False

    def synthesize(self, text: str) -> bytes:
        if not self.is_loaded:
            raise Exception("TTS no está cargado")

        try:
            wav = self.model.tts(text)
            audio_bytes = self.model.save_wav_to_bytes(wav)
            return audio_bytes
        except Exception as e:
            logger.error(f"❌ Error en TTS: {e}")
            raise Exception(f"Error generando voz: {str(e)}")


tts_service = TTSService()
