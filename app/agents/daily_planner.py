from typing import List
from app.agents.base import BaseAgent
from app.workflow.events import StopEvent
from app.artifacts.context import ContextArtifact
from app.artifacts.itinerary import DayPlan, ItineraryArtifact
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

class DailyPlannerAgent(BaseAgent):
    def __init__(self, llm: OpenAI, verbose: bool = False):
        super().__init__(llm, verbose)
        self.planning_prompt = PromptTemplate(
            template="""
            Create a detailed day-by-day travel itinerary for:
            Destination: {destination}
            Duration: {duration} days
            Group Size: {group_size}
            Budget: {budget}
            Preferences: {preferences}

            For each day, provide:
            1. Main Location: Specify the county and district where most activities will take place
            2. Activities: List of activities with:
               - Times
               - Descriptions
               - Specific locations (county, district, and coordinates if known)
            3. Meals: List of meals with:
               - Times
               - Descriptions
               - Restaurant locations
            4. Transit: Transportation details between locations
            
            """
        )

    async def process(self, context: ContextArtifact) -> StopEvent:
        """Generate daily plans based on travel context."""
        try:
            # Generate daily plans
            daily_plans = await self.llm.astructured_predict(
                List[DayPlan],
                self.planning_prompt,
                **context.model_dump()
            )

            # Create itinerary artifact
            itinerary = ItineraryArtifact(
                destination=context.destination,
                duration=context.duration,
                daily_plans=daily_plans
            )
            
            return StopEvent(content=itinerary)
            
        except Exception as e:
            self._log_verbose(f"Error generating daily plans: {str(e)}")
            return StopEvent(
                result={
                    "status": "error",
                    "message": "Failed to generate daily plans. Please try again."
                }
            )

    async def update_plans(
        self,
        existing_itinerary: ItineraryArtifact,
        updated_context: ContextArtifact
    ) -> StopEvent:
        """Update existing plans with new context."""
        try:
            # Generate new plans with updated context
            new_plans = await self.llm.astructured_predict(
                List[DayPlan],
                self.planning_prompt,
                **updated_context.model_dump()
            )

            # Update existing itinerary
            existing_itinerary.update_daily_plans(new_plans)
            
            return StopEvent(content=existing_itinerary)
            
        except Exception as e:
            self._log_verbose(f"Error updating daily plans: {str(e)}")
            return StopEvent(
                result={
                    "status": "error",
                    "message": "Failed to update daily plans. Please try again."
                }
            )