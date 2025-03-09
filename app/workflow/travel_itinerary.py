from typing import Any, Union, Optional, Dict
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import Workflow, Context, StartEvent, StopEvent, step
from app.workflow.models import (
    IntentType
)
from app.agents import (
    IntentionDetectionAgent,
    ContextExtractionAgent,
    DailyPlannerAgent,
    # HotelRecommenderAgent,
    # ItineraryIntegratorAgent,
    # ItineraryEvaluatorAgent
)
from app.workflow.events import (
    IntentionEvent,
    ContextExtractionEvent,
    # PlanGenerationEvent,
    # HotelRecommendationEvent,
    # IntegrationEvent
)
from app.artifacts.context import ContextArtifact
from app.artifacts.itinerary import ItineraryArtifact

class TravelItineraryWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        existing_context: Optional[Dict] = None,
        existing_itinerary: Optional[Dict] = None,
        verbose: bool = False,
        timeout: float = 200.0,    
        **kwargs: Any
    ) -> None:
        """
        Initialize the TravelItineraryWorkflow.

        Args:
            *args: Additional arguments to pass to the Workflow constructor.
            existing_context: Existing context for the workflow.
            existing_itinerary: Existing itinerary for the workflow.
            verbose: Whether to print verbose output.
            timeout: Timeout in seconds for workflow execution. Default is 200 seconds.
            **kwargs: Additional keyword arguments to pass to the Workflow constructor.
        """
        super().__init__(*args, timeout=timeout, **kwargs)
        self.verbose = verbose
        
        # Initialize agents
        self.intention_agent = IntentionDetectionAgent(llm=OpenAI(model="gpt-4o-mini", temperature=0.7), verbose=verbose)
        self.context_agent = ContextExtractionAgent(llm=OpenAI(model="gpt-4o-mini", temperature=0.7), verbose=verbose)
        self.planner_agent = DailyPlannerAgent(llm=OpenAI(model="gpt-4o-mini", temperature=0.7), verbose=verbose)
        # self.hotel_agent = HotelRecommenderAgent(llm=OpenAI(model="gpt-4o-mini", temperature=0.7), verbose=verbose)
        # self.integrator_agent = ItineraryIntegratorAgent(llm=OpenAI(model="gpt-4o-mini", temperature=0.7), verbose=verbose)

        # Set existing artifacts if provided
        self.existing_context = ContextArtifact(**existing_context) if existing_context else None
        self.existing_itinerary = ItineraryArtifact(**existing_itinerary) if existing_itinerary else None

    @step
    async def detect_intention(self, ctx: Context, ev: StartEvent) -> Union[IntentionEvent, StopEvent]:
        """Detect the intention of the user's query."""
        # Store original query
        await ctx.set("original_query", ev.query)
        
        # Detect intention
        return await self.intention_agent.process(ev.query)
    
    @step
    async def extract_context(
        self, 
        ctx: Context, 
        ev: IntentionEvent
    ) -> Union[ContextExtractionEvent, StopEvent]:
        """Extract or update context based on detected intention."""
        original_query = await ctx.get("original_query")
        
        if ev.intent_type == IntentType.NEW_TRIP.value:
            return await self.context_agent.process(original_query)
            
        elif ev.intent_type == IntentType.UPDATE_ITINERARY.value:
            if not self.existing_context:
                return StopEvent(
                    result={
                        "status": "error",
                        "message": "No existing itinerary to update. Would you like to create a new trip plan?"
                    }
                )
            
            return await self.context_agent.update_context(
                self.existing_context,
                original_query,
                ev.update_target or "general"
            )
            
        else:
            return StopEvent(
                result={
                    "status": "unrelated",
                    "message": "I can help you plan a trip or update your existing travel plans. What would you like to do?"
                }
            )
    
    @step
    async def generate_daily_plans(self, ctx: Context, ev: ContextExtractionEvent) -> StopEvent:
        """Generate daily itinerary plans or update existing plans."""
        if self.existing_itinerary:
            # Update existing itinerary with new context
            return await self.planner_agent.update_plans(
                self.existing_itinerary,
                ev.context
            )
        else:
            # Generate new plans from scratch
            return await self.planner_agent.process(ev.context)

    # @step
    # async def recommend_hotels(self, ctx: Context, ev: PlanGenerationEvent) -> HotelRecommendationEvent:
    #     """Generate hotel recommendations based on itinerary."""
    #     if self.existing_itinerary and self.existing_itinerary.hotel_recommendations:
    #         # Update existing hotel recommendations
    #         updated_itinerary = await self.hotel_agent.update_recommendations(
    #             ev.content
    #         )
    #         return HotelRecommendationEvent(content=updated_itinerary)
    #     else:
    #         # Generate new hotel recommendations
    #         return await self.hotel_agent.process(ev.content)

    # @step
    # async def integrate_itinerary(self, ctx: Context, ev: HotelRecommendationEvent) -> StopEvent:
    #     """Integrate and polish the complete itinerary."""
    #     final_itinerary = await self.integrator_agent.process(ev.content)
    #     return StopEvent(result=final_itinerary.dict())
        
