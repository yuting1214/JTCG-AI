from typing import Optional, List
from pydantic import BaseModel, Field
from llama_index.core.workflow import Event
from app.artifacts import ContextArtifact, ItineraryArtifact

class IntentionEvent(Event):
    """Event containing detected user intention."""
    event_id: str = Field(..., description="Unique identifier for the intention event")
    intent_type: str = Field(..., description="Type of intention detected")
    confidence: float = Field(..., description="Confidence score of intention detection")
    action_required: Optional[str] = Field(None, description="Specific action required")
    update_target: Optional[str] = Field(None, description="Target of update if applicable")

class ContextExtractionEvent(Event):
    context: ContextArtifact

class PlanGenerationEvent(Event):
    content: ItineraryArtifact

class HotelRecommendationEvent(Event):
    content: ItineraryArtifact

class IntegrationEvent(Event):
    content: ItineraryArtifact

class EvaluationEvent(Event):
    content: ItineraryArtifact
    status: str

class StopEvent(Event):
    result: dict