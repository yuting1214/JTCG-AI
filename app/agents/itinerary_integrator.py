# # app/agents/itinerary_integrator.py
# from app.agents.base import BaseAgent
# from app.models.events import EvaluationEvent
# from app.models.itinerary import ItineraryContent
# from llama_index.core import PromptTemplate

# class ItineraryIntegratorAgent(BaseAgent):
#     async def process(self, content: ItineraryContent) -> EvaluationEvent:
#         """Integrate and polish the complete itinerary."""
#         integration_prompt = PromptTemplate(
#             template="""
#             Create a cohesive travel itinerary summary integrating the following components:

#             DESTINATION: {destination}
#             DURATION: {duration} days
#             GROUP: {group_size} travelers
#             PREFERENCES: {preferences}

#             DAILY ACTIVITIES:
#             {daily_activities}

#             RECOMMENDED HOTELS:
#             {hotel_recommendations}

#             Please provide:
#             1. A welcoming introduction highlighting key features of the trip
#             2. A day-by-day summary that flows naturally
#             3. Integrated hotel recommendations with rationale
#             4. Practical tips for transportation between activities
#             5. Special notes about dining and local experiences
#             6. Any important cultural or practical considerations

#             Make the summary engaging and personal, while maintaining all practical details.
#             """
#         )

#         # Format daily activities for the prompt
#         daily_activities = "\n".join([
#             f"Day {plan.day}:\n" + "\n".join([
#                 f"- {activity['time']}: {activity['description']}"
#                 for activity in plan.activities
#             ])
#             for plan in content.daily_plans
#         ])

#         # Format hotel recommendations
#         hotel_details = "\n".join([
#             f"- {hotel.name} ({hotel.price_range}): {hotel.description}"
#             for hotel in content.hotel_recommendations
#         ])

#         summary = await self.llm.acomplete(
#             integration_prompt,
#             destination=content.context.destination,
#             duration=content.context.duration,
#             group_size=content.context.group_size,
#             preferences=content.context.preferences,
#             daily_activities=daily_activities,
#             hotel_recommendations=hotel_details
#         )

#         content.summary = summary.text
#         self._log_verbose("Generated integrated itinerary summary")
        
#         return EvaluationEvent(content=content, status="complete")