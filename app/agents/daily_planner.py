from typing import List, Dict, Any
from datetime import date
from app.agents.base import BaseAgent
from app.workflow.models import TravelItinerary
from app.workflow.events import StopEvent, PlanGenerationEvent
from app.artifacts.context import ContextArtifact
from app.artifacts.itinerary import ItineraryArtifact
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
                1. Day number and date
                2. Main location (county and district)
                3. Schedule as a chronological list of events, where each event has:
                - time (in 24-hour format, e.g. "09:00")
                - type ("activity", "meal", or "transit")
                - description (what to do/eat/how to move)
                - location (county and district)

                Example day format:
                {
                    "day": 1,
                    "date": "2024-03-20",
                    "location": {"county": "台北市", "district": "信義區"},
                    "schedule": [
                        {
                            "time": "09:00",
                            "type": "meal",
                            "description": "Traditional breakfast at Fu Hang Soy Milk",
                            "location": "台北市中正區"
                        },
                        {
                            "time": "10:30",
                            "type": "activity",
                            "description": "Visit Taipei 101 Observation Deck",
                            "location": "台北市信義區"
                        },
                        {
                            "time": "12:00",
                            "type": "transit",
                            "description": "Take MRT from Taipei 101 to Ximen",
                            "location": "台北市信義區到萬華區"
                        }
                    ]
                }

            Ensure:
            - Activities are reasonably spaced
            - Include breakfast, lunch, and dinner
            - Account for travel time between locations
            - Stay within daily budget
            """
    )

    def _prepare_prompt_variables(self, context: ContextArtifact) -> Dict[str, Any]:
        """Prepare and validate all variables needed for the prompt"""
        start_date = date.today() # Default to start Today
        
        return {
            "destination": getattr(context, "destination", "Unknown"),
            "duration": getattr(context, "duration", 1),
            "start_date": start_date.isoformat(),
            "group_size": getattr(context, "group_size", 1),
            "budget": getattr(context, "budget", "flexible"),
            "preferences": getattr(context, "preferences", "standard travel preferences")
        }


    async def process(self, context: ContextArtifact) -> PlanGenerationEvent:
        """Generate daily plans based on travel context."""
        try:
    
            # Prepare prompt variables with defaults
            prompt_vars = self._prepare_prompt_variables(context)

            # Generate daily plans
            daily_plans = await self.llm.astructured_predict(
                TravelItinerary,
                self.planning_prompt,
                **prompt_vars
            )

            self._log_verbose(f"Step - DailyPlannerAgent: Daily plans generated - {daily_plans}")

            # Create itinerary artifact
            itinerary = ItineraryArtifact(
                itinerary=daily_plans
            )
            
            return PlanGenerationEvent(content=itinerary)
            
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
    ) -> PlanGenerationEvent:
        """Update existing plans with new context."""
        try:
            # Prepare prompt variables with defaults
            prompt_vars = self._prepare_prompt_variables(updated_context)
            
            if existing_itinerary.itinerary:
                prompt_vars["start_date"] = existing_itinerary.itinerary.start_date.isoformat()

            # Generate new plans with updated context
            new_itinerary = await self.llm.astructured_predict(
                TravelItinerary,
                self.planning_prompt,
                **prompt_vars
            )

            # Update existing itinerary
            existing_itinerary.update_itinerary(new_itinerary)
            
            return PlanGenerationEvent(content=existing_itinerary)
            
        except Exception as e:
            self._log_verbose(f"Error updating daily plans: {str(e)}")
            return StopEvent(
                result={
                    "status": "error",
                    "message": "Failed to update daily plans. Please try again."
                }
            )