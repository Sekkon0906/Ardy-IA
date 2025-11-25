"""
Speech-to-Text service using Faster Whisper
"""
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

# Intentar importar Whisper de forma segura
try:
    from faster_whisper import WhisperModel  # type: ignore
    WHISPER_AVAILABLE = True
    logger.info("Faster Whisper importado correctamente.")
except Exception as e:
    logger.error(f"Whisper no disponible. Error al importar faster_whisper: {e}")
    WHISPER_AVAILABLE = False

from backend.config import settings


class STTService:
    def __init__(self) -> None:
        self.model: WhisperModel | None = None
        self.is_loaded: bool = False

    def load_model(self) -> None:
        """Carga el modelo Whisper al iniciar la aplicación."""
        if not WHISPER_AVAILABLE:
            logger.warning("⚠️ Whisper no disponible - funcionalidad de transcripción desactivada")
            return

        try:
            logger.info("Loading Whisper model: %s", settings.WHISPER_MODEL)
            self.model = WhisperModel(
                settings.WHISPER_MODEL,
                device="cpu",
                compute_type="int8",
            )
            self.is_loaded = True
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error("❌ Failed to load Whisper: %s", e)
            logger.warning("⚠️ Continuando sin funcionalidad de transcripción")
            self.is_loaded = False

    async def transcribe(self, audio_file: bytes, language: str | None = None) -> str:
        """
        Transcribe audio a texto.
        """
        if not WHISPER_AVAILABLE or not self.is_loaded or self.model is None:
            raise Exception("Servicio de transcripción no disponible")

        # Validación básica
        if not audio_file:
            raise Exception("No se recibió audio")

        audio_len = len(audio_file)
        if audio_len < 500:
            # Demasiado pequeño, casi seguro que está vacío o corrupto
            logger.warning("Audio muy corto (len=%s).", audio_len)
            raise Exception("Archivo de audio demasiado corto")

        # Si es pequeño pero razonable, intentamos igualmente
        if audio_len < 4000:
            logger.warning("Audio relativamente corto (len=%s). Intentando transcribir igualmente.", audio_len)

        tmp_path = None
        try:
            # Guardar audio en archivo temporal (usamos .webm porque el front envía WebM)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                tmp_file.write(audio_file)
                tmp_path = tmp_file.name

            segments, info = self.model.transcribe(
                tmp_path,
                language=language,
                beam_size=5,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500},
            )

            transcription = " ".join(segment.text for segment in segments).strip()
            logger.info("🎤 Transcribed (%s): %s...", info.language, transcription[:50])
            return transcription

        except Exception as e:
            logger.error("❌ Transcription failed: %s", e)
            raise Exception(f"Error de transcripción: {e}") from e
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass


# Singleton instance
stt_service = STTService()
