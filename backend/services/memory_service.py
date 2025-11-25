"""
Persistent conversation memory with SQLite
"""
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class ConversationMessage(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True)
    role = Column(String(20))  # user, assistant
    content = Column(Text)
    language = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    message_count = Column(Integer, default=0)


class MemoryService:
    def __init__(self):
        # FIX: Manejo correcto de la URL de base de datos
        db_url = settings.DATABASE_URL
        if db_url.startswith("sqlite+aiosqlite"):
            # Convertir a sqlite sync para SQLAlchemy normal
            db_url = db_url.replace("sqlite+aiosqlite", "sqlite")
        
        self.engine = create_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False}  # FIX: Necesario para SQLite en Windows
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("✅ Memory service initialized")
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def add_message(self, session_id: str, role: str, content: str, language: str = "es"):
        """Add message to conversation history"""
        db = self.SessionLocal()
        try:
            # Add message
            message = ConversationMessage(
                session_id=session_id,
                role=role,
                content=content,
                language=language
            )
            db.add(message)
            
            # Update or create session
            session = db.query(Session).filter(Session.session_id == session_id).first()
            if session:
                session.last_activity = datetime.utcnow()
                session.message_count += 1
            else:
                session = Session(
                    session_id=session_id,
                    message_count=1
                )
                db.add(session)
            
            db.commit()
            logger.debug(f"💾 Saved message: {session_id} - {role}")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Failed to save message: {e}")
        finally:
            db.close()
    
    def get_conversation_history(self, session_id: str, limit: int = None) -> List[Dict]:
        """Get conversation history for session"""
        db = self.SessionLocal()
        try:
            query = db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session_id
            ).order_by(ConversationMessage.timestamp.desc())
            
            if limit:
                query = query.limit(limit)
            
            messages = query.all()
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in reversed(messages)
            ]
        finally:
            db.close()
    
    def get_context_string(self, session_id: str, max_messages: int = 10) -> str:
        """Get formatted conversation context"""
        history = self.get_conversation_history(session_id, limit=max_messages)
        if not history:
            return ""
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    
    def cleanup_old_sessions(self):
        """Remove sessions older than configured timeout"""
        db = self.SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=settings.SESSION_TIMEOUT_HOURS)
            old_sessions = db.query(Session).filter(Session.last_activity < cutoff).all()
            
            for session in old_sessions:
                # Delete messages
                db.query(ConversationMessage).filter(
                    ConversationMessage.session_id == session.session_id
                ).delete()
                # Delete session
                db.delete(session)
            
            db.commit()
            logger.info(f"🗑️ Cleaned up {len(old_sessions)} old sessions")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Cleanup failed: {e}")
        finally:
            db.close()


# Singleton instance
memory_service = MemoryService()