from typing import Any, Union, Optional, Dict
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import Workflow, Context, StartEvent, StopEvent, step
from app.agents import (
    ContextExtractionAgent,
    DailyPlannerAgent,
    HotelRecommenderAgent,
    ItineraryIntegratorAgent,
    ItineraryEvaluatorAgent
)
from app.workflow.events import (
    ContextExtractionEvent,
    PlanGenerationEvent,
    HotelRecommendationEvent,
    IntegrationEvent
)
from app.artifacts.context import ContextArtifact
from app.artifacts.itinerary import ItineraryArtifact

class TravelItineraryWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        verbose: bool = False,
        existing_context: Optional[Dict] = None,
        existing_itinerary: Optional[Dict] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.llm = OpenAI(model="gpt-4", temperature=0.7)
        self.verbose = verbose
        
        # Initialize agents
        self.context_agent = ContextExtractionAgent(llm=self.llm, verbose=verbose)
        self.planner_agent = DailyPlannerAgent(llm=self.llm, verbose=verbose)
        self.hotel_agent = HotelRecommenderAgent(llm=self.llm, verbose=verbose)
        self.integrator_agent = ItineraryIntegratorAgent(llm=self.llm, verbose=verbose)

        # Set existing artifacts if provided
        self.existing_context = ContextArtifact(**existing_context) if existing_context else None
        self.existing_itinerary = ItineraryArtifact(**existing_itinerary) if existing_itinerary else None

    @step
    async def extract_context(self, ctx: Context, ev: StartEvent) -> Union[ContextExtractionEvent, StopEvent]:
        """Extract travel context from user query or update existing context."""
        if self.existing_context:
            # Update existing context with new information from query
            updated_context = await self.context_agent.update_context(
                self.existing_context, 
                ev.query
            )
            return ContextExtractionEvent(context=updated_context)
        else:
            # Extract new context from scratch
            return await self.context_agent.process(ev.query)

    @step
    async def generate_daily_plans(self, ctx: Context, ev: ContextExtractionEvent) -> PlanGenerationEvent:
        """Generate daily itinerary plans or update existing plans."""
        if self.existing_itinerary:
            # Update existing itinerary with new context
            updated_itinerary = await self.planner_agent.update_plans(
                self.existing_itinerary,
                ev.context
            )
            return PlanGenerationEvent(content=updated_itinerary)
        else:
            # Generate new plans from scratch
            return await self.planner_agent.process(ev.context)

    @step
    async def recommend_hotels(self, ctx: Context, ev: PlanGenerationEvent) -> HotelRecommendationEvent:
        """Generate hotel recommendations based on itinerary."""
        if self.existing_itinerary and self.existing_itinerary.hotel_recommendations:
            # Update existing hotel recommendations
            updated_itinerary = await self.hotel_agent.update_recommendations(
                ev.content
            )
            return HotelRecommendationEvent(content=updated_itinerary)
        else:
            # Generate new hotel recommendations
            return await self.hotel_agent.process(ev.content)

    @step
    async def integrate_itinerary(self, ctx: Context, ev: HotelRecommendationEvent) -> StopEvent:
        """Integrate and polish the complete itinerary."""
        final_itinerary = await self.integrator_agent.process(ev.content)
        return StopEvent(result=final_itinerary.dict())
        
    async def process_message(self, message: str) -> Dict:
        """Process a message and return the appropriate response based on workflow state."""
        # Create a start event with the user's message
        start_event = StartEvent(query=message)
        
        # Run the workflow
        result = await self.run(start_event)
        
        return result
