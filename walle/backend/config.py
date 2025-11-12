"""
Configuration management for WALL-E AI
CONFIGURADO: Usa gemma:2b como modelo principal
"""
from pydantic_settings import BaseSettings
from typing import List
import os

# Desactivar telemetría de ChromaDB
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"


class Settings(BaseSettings):
    # Ollama - MODELO: gemma:2b (ligero y rápido)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma:2b"  # ✅ Modelo Gemma 2B

    # Whisper
    WHISPER_MODEL: str = "base"
    
    # TTS (opcional)
    TTS_MODEL: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./walle.db"
    
    # RAG
    CHROMADB_PATH: str = "./chromadb_data"
    MAX_SEARCH_RESULTS: int = 3
    EMBEDDING_MODEL: str = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
    
    # Memory
    MAX_MEMORY_MESSAGES: int = 20
    SESSION_TIMEOUT_HOURS: int = 24
    
    # ChromaDB Telemetry (desactivada)
    ANONYMIZED_TELEMETRY: bool = False
    CHROMA_TELEMETRY_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()