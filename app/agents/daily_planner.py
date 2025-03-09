from app.agents.base import BaseAgent
from app.models.events import PlanGenerationEvent
from app.models.itinerary import DailyPlan, ItineraryContent
from llama_index.core import PromptTemplate

class DailyPlannerAgent(BaseAgent):
    async def process(self, context: TravelContext) -> PlanGenerationEvent:
        planning_prompt = PromptTemplate(
            template="""
            Create a detailed day-by-day travel itinerary for:
            Destination: {destination}
            Duration: {duration} days
            Group Size: {group_size}
            Budget: {budget}
            Preferences: {preferences}

            For each day, provide:
            1. Morning activities
            2. Lunch recommendations
            3. Afternoon activities
            4. Dinner recommendations
            5. Evening activities
            6. Transportation details

            Return as a structured JSON array of daily plans.
            """
        )

        daily_plans = await self.llm.astructured_predict(
            List[DailyPlan],
            planning_prompt,
            **context.dict()
        )

        content = ItineraryContent(
            context=context,
            daily_plans=daily_plans
        )
        
        return PlanGenerationEvent(content=content)