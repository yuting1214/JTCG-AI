from pydantic import BaseModel
from app.artifacts import ContextArtifact, ItineraryArtifact

class StartEvent(BaseModel):
    query: str

class ContextExtractionEvent(BaseModel):
    context: ContextArtifact

class PlanGenerationEvent(BaseModel):
    content: ItineraryArtifact

class HotelRecommendationEvent(BaseModel):
    content: ItineraryArtifact

class IntegrationEvent(BaseModel):
    content: ItineraryArtifact

class EvaluationEvent(BaseModel):
    content: ItineraryArtifact
    status: str

class StopEvent(BaseModel):
    result: dict