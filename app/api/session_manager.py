from typing import Dict, Optional
from uuid import UUID
from app.api.models import SessionState
from app.artifacts.context import ContextArtifact
from app.artifacts.itinerary import ItineraryArtifact

class SessionManager:
    """Manages conversation sessions and their states"""
    
    def __init__(self):
        self.sessions: Dict[UUID, SessionState] = {}
    
    def create_session(self) -> SessionState:
        """Create a new session"""
        session = SessionState()
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: UUID) -> Optional[SessionState]:
        """Get an existing session by ID"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: UUID, 
                      context: Optional[ContextArtifact] = None,
                      itinerary: Optional[ItineraryArtifact] = None,
                      current_step: Optional[str] = None) -> SessionState:
        """Update session with new data"""
        session = self.sessions[session_id]
        
        if context:
            session.context = context.dict()
        
        if itinerary:
            session.itinerary = itinerary.dict()
            
        if current_step:
            session.current_step = current_step
            
        return session
    
    def add_message_to_history(self, session_id: UUID, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        if session_id in self.sessions:
            self.sessions[session_id].conversation_history.append({
                "role": role,
                "content": content
            })
    
    def delete_session(self, session_id: UUID) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# Global session manager instance
session_manager = SessionManager()