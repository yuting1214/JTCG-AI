from typing import Union
import uuid
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
from app.agents.base import BaseAgent
from app.workflow.events import IntentionEvent, StopEvent
from app.workflow.models import IntentionAnalysis

class IntentionDetectionAgent(BaseAgent):
    def __init__(self, llm: OpenAI, verbose: bool = False):
        super().__init__(llm, verbose)
        self.intent_prompt = PromptTemplate(
            template="""
            Analyze the following user message and determine its intention in the context of travel planning:

            User Message: {query}

            Determine:
            1. Is this a new trip request, an update to existing plans, a response to clarification, or unrelated?
            2. If it's an update, what aspect is being updated? (activities, hotels, dates, etc.)
            3. How confident are you in this classification?

            Return a JSON object with:
            {
                "intent_type": "new_trip" | "update_itinerary" | "clarification_response" | "unrelated",
                "confidence": <float between 0 and 1>,
                "action_required": <string, optional>,
                "update_target": <string, optional>
            }
            """
        )

    async def process(self, query: str) -> Union[IntentionEvent, StopEvent]:
        """Detect the intention of the user's query."""
        try:
            analysis = await self.llm.astructured_predict(
                IntentionAnalysis,
                self.intent_prompt,
                query=query
            )
            
            if analysis.confidence < 0.5:
                self._log_verbose(f"Low confidence in intention detection: {analysis.confidence}")
                return StopEvent(
                    event_id=str(uuid.uuid4()),
                    result={
                        "status": "low_confidence",
                        "message": "I'm not sure what you'd like to do. Could you please rephrase your request?"
                    }
                )
            else:
                self._log_verbose(f"Step - IntentionDetectionAgent: Intention detection successful: {analysis}")

            return IntentionEvent(
                event_id=str(uuid.uuid4()),
                intent_type=analysis.intent_type,
                confidence=analysis.confidence,
                action_required=analysis.action_required,
                update_target=analysis.update_target
            )

        except Exception as e:
            self._log_verbose(f"Error in intention detection: {str(e)}")
            return StopEvent(
                event_id=str(uuid.uuid4()),
                result={
                    "error": f"Failed to analyze intention: {str(e)}",
                    "status": "error"
                }
            )