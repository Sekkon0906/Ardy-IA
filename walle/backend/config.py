"""
Configuration management for WALL-E AI
MODIFIÉ: Utilise Groq (GRATUIT et ILLIMITÉ)
"""
from pydantic_settings import BaseSettings
from typing import List
import os

# Désactiver télémétrie de ChromaDB
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"


class Settings(BaseSettings):
    # ========================================
    # CONFIGURATION GROQ (GRATUIT)
    # ========================================
    # Obtenir une clé gratuite sur: https://console.groq.com/
    GROQ_API_KEY: str = !
    
    # Modèles disponibles gratuitement sur Groq:
    # - llama-3.1-70b-versatile (recommandé - très intelligent)
    # - llama-3.1-8b-instant (ultra-rapide)
    # - mixtral-8x7b-32768 (bon équilibre)
    # - gemma2-9b-it (léger et efficace)
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    
    # Paramètres du modèle
    MODEL_TEMPERATURE: float = 0.8
    MODEL_MAX_TOKENS: int = 500
    
    # Whisper (STT) - optionnel
    WHISPER_MODEL: str = "base"
    
    # TTS - optionnel
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
    
    # ChromaDB Telemetry (désactivée)
    ANONYMIZED_TELEMETRY: bool = False
    CHROMA_TELEMETRY_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
