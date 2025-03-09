# # app/agents/hotel_recommender.py
# from typing import List
# from app.agents.base import BaseAgent
# from app.models.events import HotelRecommendationEvent
# from app.models.itinerary import ItineraryContent, HotelRecommendation
# from llama_index.core import PromptTemplate

# class HotelRecommenderAgent(BaseAgent):
#     async def process(self, content: ItineraryContent) -> HotelRecommendationEvent:
#         """Generate hotel recommendations based on itinerary content."""
#         hotel_prompt = PromptTemplate(
#             template="""
#             Based on the following travel details, recommend 3 suitable hotels:

#             Destination: {destination}
#             Duration: {duration} days
#             Budget: {budget}
#             Group Size: {group_size}
#             Key Activities Areas: {activity_areas}

#             Important Considerations:
#             - Proximity to planned activities
#             - Group size accommodation
#             - Budget constraints
#             - Preferred amenities based on traveler profile

#             For each hotel, provide:
#             1. Hotel name
#             2. Location and proximity to key areas
#             3. Price range per night
#             4. Key amenities
#             5. Brief description highlighting why it suits this itinerary

#             Format as a structured JSON array of hotel recommendations.
#             """
#         )

#         # Extract key activity areas from daily plans
#         activity_areas = set()
#         for plan in content.daily_plans:
#             for activity in plan.activities:
#                 if 'location' in activity:
#                     activity_areas.add(activity['location'])

#         hotels = await self.llm.astructured_predict(
#             List[HotelRecommendation],
#             hotel_prompt,
#             destination=content.context.destination,
#             duration=content.context.duration,
#             budget=content.context.budget,
#             group_size=content.context.group_size,
#             activity_areas=list(activity_areas)
#         )

#         content.hotel_recommendations = hotels
#         self._log_verbose(f"Generated {len(hotels)} hotel recommendations")
        
#         return HotelRecommendationEvent(content=content)