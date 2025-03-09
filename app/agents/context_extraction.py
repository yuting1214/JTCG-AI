# app/agents/context_extraction.py
from app.agents.base import BaseAgent
from app.models.events import ContextExtractionEvent, StopEvent
from app.models.itinerary import TravelContext
from llama_index.core import PromptTemplate

class ContextExtractionAgent(BaseAgent):
    async def process(self, query: str) -> Union[ContextExtractionEvent, StopEvent]:
        context_prompt = PromptTemplate(
            template="""
            Extract travel planning details from the following query:
            {query}
            
            Extract and return a JSON object with:
            - destination (string)
            - duration (integer, in days)
            - group_size (integer)
            - budget (string, optional)
            - preferences (list of strings)
            """
        )

        try:
            context = await self.llm.astructured_predict(
                TravelContext,
                context_prompt,
                query=query
            )
            self._log_verbose(f"Extracted context: {context}")
            return ContextExtractionEvent(context=context)
        except Exception as e:
            return StopEvent(result={"error": f"Failed to extract context: {str(e)}"})