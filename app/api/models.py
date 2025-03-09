from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

class ConversationRequest(BaseModel):
    """Request model for conversation API"""
    message: str
    session_id: Optional[UUID] = None  # None for new conversations, UUID for existing ones
    
class ConversationResponse(BaseModel):
    """Response model for conversation API"""
    session_id: UUID
    message: str
    itinerary: Optional[Dict[str, Any]] = None
    status: str = "in_progress"  # Can be "in_progress" or "complete"
    
class SessionState(BaseModel):
    """Internal model to track session state"""
    session_id: UUID = uuid4()
    context: Optional[Dict[str, Any]] = None
    itinerary: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, str]] = []
    current_step: str = "extract_context"  # Track workflow progress