"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User's message")
    lang: str = Field(default="es", description="Language code (es, en, fr)")
    session_id: Optional[str] = Field(None, description="Session identifier")
    use_rag: bool = Field(default=True, description="Enable RAG search")


class AudioRequest(BaseModel):
    session_id: Optional[str] = None
    lang: str = "es"
    use_rag: bool = True


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    correction: Optional[str] = None
    explanation: Optional[str] = None
    memory: List[Dict[str, str]] = []
    rag_used: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AudioResponse(BaseModel):
    transcription: str
    answer: str
    session_id: str
    audio_url: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    whisper_loaded: bool
    tts_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    message_count: int
    last_activity: datetime