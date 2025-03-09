# # app/agents/itinerary_evaluator.py
# from typing import Dict, List
# from app.agents.base import BaseAgent
# from app.models.events import StopEvent
# from app.models.itinerary import ItineraryContent
# from llama_index.core import PromptTemplate
# from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator

# class ItineraryEvaluatorAgent(BaseAgent):
#     def __init__(self, llm: OpenAI, verbose: bool = False):
#         super().__init__(llm, verbose)
#         self.faithfulness_evaluator = FaithfulnessEvaluator(llm=llm)
#         self.relevancy_evaluator = RelevancyEvaluator(llm=llm)

#     async def process(self, content: ItineraryContent) -> StopEvent:
#         """Evaluate the generated itinerary for quality and relevance."""
#         evaluation_results = {
#             "daily_plans": await self._evaluate_daily_plans(content),
#             "hotel_recommendations": await self._evaluate_hotels(content),
#             "overall_assessment": await self._evaluate_overall(content)
#         }

#         result = {
#             "itinerary": content.dict(),
#             "evaluation": evaluation_results
#         }

#         self._log_verbose("Completed itinerary evaluation")
#         return StopEvent(result=result)

#     async def _evaluate_daily_plans(self, content: ItineraryContent) -> List[Dict]:
#         """Evaluate each day's activities for feasibility and alignment with preferences."""
#         daily_evaluations = []
        
#         for plan in content.daily_plans:
#             # Evaluate faithfulness to preferences
#             faith_eval = await self.faithfulness_evaluator.aevaluate(
#                 query=f"Day {plan.day} activities matching preferences",
#                 response=str(plan.activities),
#                 contexts=[str(content.context.preferences)]
#             )
            
#             # Evaluate feasibility of timing and logistics
#             feasibility_prompt = PromptTemplate(
#                 template="""
#                 Evaluate the feasibility of this day plan in {destination}:
#                 {activities}

#                 Consider:
#                 1. Time allocations
#                 2. Travel distances
#                 3. Opening hours
#                 4. Physical demands
#                 5. Weather considerations

#                 Rate feasibility from 1-10 and provide specific concerns if any.
#                 """
#             )
            
#             feasibility = await self.llm.astructured_predict(
#                 dict,
#                 feasibility_prompt,
#                 destination=content.context.destination,
#                 activities=str(plan.activities)
#             )

#             daily_evaluations.append({
#                 "day": plan.day,
#                 "preference_alignment": faith_eval.score,
#                 "feasibility_score": feasibility.get("score", 0),
#                 "concerns": feasibility.get("concerns", [])
#             })

#         return daily_evaluations

#     async def _evaluate_hotels(self, content: ItineraryContent) -> Dict:
#         """Evaluate hotel recommendations for suitability."""
#         hotel_eval_prompt = PromptTemplate(
#             template="""
#             Evaluate these hotel recommendations for a {duration}-day stay in {destination}:
#             Group Size: {group_size}
#             Budget: {budget}
#             Hotels: {hotels}

#             Evaluate:
# 1. Budget alignment
# 2. Location convenience
# 3. Group accommodation suitability
# 4. Amenity relevance

#             Provide scores (1-10) and specific feedback for each criterion.
#             """
#         )

#         evaluation = await self.llm.astructured_predict(
#             dict,
#             hotel_eval_prompt,
#             duration=content.context.duration,
#             destination=content.context.destination,
#             group_size=content.context.group_size,
#             budget=content.context.budget,
#             hotels=str(content.hotel_recommendations)
#         )

#         return evaluation

#     async def _evaluate_overall(self, content: ItineraryContent) -> Dict:
#         """Provide overall itinerary assessment."""
#         overall_prompt = PromptTemplate(
#             template="""
#             Provide a comprehensive assessment of this travel itinerary:
#             {summary}

#             Evaluate:
#             1. Preference alignment
#             2. Pace and flow
#             3. Activity variety
#             4. Cultural immersion
#             5. Practical considerations

#             Provide:
#             1. Scores for each criterion (1-10)
#             2. Key strengths
#             3. Areas for improvement
#             4. Overall rating
#             """
#         )

#         assessment = await self.llm.astructured_predict(
#             dict,
#             overall_prompt,
#             summary=content.summary
#         )

#         return assessment