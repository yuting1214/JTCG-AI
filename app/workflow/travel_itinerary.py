# app/workflows/travel_itinerary.py
from pathlib import Path
from typing import Any
from llama_index.core.workflow import Workflow
from llama_index.llms.openai import OpenAI
from app.agents import (
    ContextExtractionAgent,
    DailyPlannerAgent,
    HotelRecommenderAgent,
    ItineraryIntegratorAgent,
    ItineraryEvaluatorAgent
)
from app.models.events import (
    StartEvent,
    ContextExtractionEvent,
    PlanGenerationEvent,
    HotelRecommendationEvent,
    IntegrationEvent,
    EvaluationEvent,
    StopEvent
)

class TravelItineraryWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        output_dir: str = "./data/itineraries",
        verbose: bool = False,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.llm = OpenAI(model="gpt-4", temperature=0.7)
        self.verbose = verbose
        self.output_dir = Path(output_dir)
        
        # Initialize agents
        self.context_agent = ContextExtractionAgent(llm=self.llm, verbose=verbose)
        self.planner_agent = DailyPlannerAgent(llm=self.llm, verbose=verbose)
        self.hotel_agent = HotelRecommenderAgent(llm=self.llm, verbose=verbose)
        self.integrator_agent = ItineraryIntegratorAgent(llm=self.llm, verbose=verbose)
        self.evaluator_agent = ItineraryEvaluatorAgent(llm=self.llm, verbose=verbose)

    @step
    async def extract_context(self, ctx: Context, ev: StartEvent) -> Union[ContextExtractionEvent, StopEvent]:
        """Extract travel context from user query."""
        return await self.context_agent.process(ev.query)

    @step
    async def generate_daily_plans(self, ctx: Context, ev: ContextExtractionEvent) -> PlanGenerationEvent:
        """Generate daily itinerary plans."""
        return await self.planner_agent.process(ev.context)

    @step
    async def recommend_hotels(self, ctx: Context, ev: PlanGenerationEvent) -> HotelRecommendationEvent:
        """Generate hotel recommendations based on itinerary."""
        return await self.hotel_agent.process(ev.content)

    @step
    async def integrate_itinerary(self, ctx: Context, ev: HotelRecommendationEvent) -> EvaluationEvent:
        """Integrate and polish the complete itinerary."""
        return await self.integrator_agent.process(ev.content)

    @step
    async def evaluate_itinerary(self, ctx: Context, ev: EvaluationEvent) -> StopEvent:
        """Evaluate the generated itinerary for quality."""
        return await self.evaluator_agent.process(ev.content)