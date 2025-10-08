"""Session management for chat conversations."""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from app.models.schemas import MessageRole, ChatMessage, SessionResponse

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages chat sessions and conversation history."""
    
    def __init__(self, sessions_dir: str = "./data/sessions"):
        """
        Initialize session manager.
        
        Args:
            sessions_dir: Directory to store session files
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._sessions_cache: Dict[str, Dict] = {}
        logger.info(f"SessionManager initialized with directory: {self.sessions_dir}")
    
    def create_session(self, name: Optional[str] = None) -> str:
        """
        Create a new chat session.
        
        Args:
            name: Optional session name
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session_data = {
            "session_id": session_id,
            "name": name or f"Chat {now.strftime('%Y-%m-%d %H:%M')}",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "messages": []
        }
        
        # Save to file
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Cache it
        self._sessions_cache[session_id] = session_data
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        # Check cache first
        if session_id in self._sessions_cache:
            return self._sessions_cache[session_id]
        
        # Load from file
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Cache it
            self._sessions_cache[session_id] = session_data
            return session_data
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def list_sessions(self) -> List[SessionResponse]:
        """
        List all sessions.
        
        Returns:
            List of session summaries
        """
        sessions = []
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                sessions.append(SessionResponse(
                    session_id=session_data["session_id"],
                    name=session_data["name"],
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    updated_at=datetime.fromisoformat(session_data["updated_at"]),
                    message_count=len(session_data.get("messages", []))
                ))
            except Exception as e:
                logger.error(f"Error loading session file {session_file}: {e}")
                continue
        
        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        return sessions
    
    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        sources: Optional[List] = None,
        confidence: Optional[float] = None,
        web_search_used: bool = False
    ) -> ChatMessage:
        """
        Add a message to a session.
        
        Args:
            session_id: Session ID
            role: Message role (user/assistant)
            content: Message content
            sources: Optional source references
            confidence: Optional confidence score
            web_search_used: Whether web search was used
            
        Returns:
            Created message
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        now = datetime.utcnow()
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=now,
            sources=sources or [],
            confidence=confidence,
            web_search_used=web_search_used
        )
        
        # Add to session
        session["messages"].append(message.dict())
        session["updated_at"] = now.isoformat()
        
        # Save to file
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        # Update cache
        self._sessions_cache[session_id] = session
        
        return message
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session ID
            limit: Optional limit on number of messages
            
        Returns:
            List of messages
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.get("messages", [])
        
        if limit:
            messages = messages[-limit:]
        
        return [
            ChatMessage(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                sources=msg.get("sources", []),
                confidence=msg.get("confidence"),
                web_search_used=msg.get("web_search_used", False)
            )
            for msg in messages
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False if not found
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return False
        
        try:
            session_file.unlink()
            
            # Remove from cache
            if session_id in self._sessions_cache:
                del self._sessions_cache[session_id]
            
            logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False


# Global session manager instance
session_manager = SessionManager()

