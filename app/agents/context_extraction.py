from typing import Union
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
from app.agents.base import BaseAgent
from app.workflow.events import ContextExtractionEvent, StopEvent
from app.artifacts.context import ContextArtifact

class ContextExtractionAgent(BaseAgent):
    def __init__(self, llm: OpenAI, verbose: bool = False):
        super().__init__(llm, verbose)
        self.new_trip_prompt = PromptTemplate(
            template="""
            Extract travel planning information from this query:
            {query}
            
            Return a JSON object with:
            - destination (string)
            - duration (integer, in days)
            - group_size (integer)
            - budget (string, optional)
            - preferences (list of strings)
            """
        )

        self.update_prompt = PromptTemplate(
            template="""
            Update the existing travel context based on the new request.
            
            Current Context:
            {current_context}
            
            Update Request:
            {query}
            
            Update Target: {update_target}

            Return the complete updated JSON object with all fields.
            """
        )

    async def process(self, query: str) -> Union[ContextExtractionEvent, StopEvent]:
        """Extract new travel context from query."""
        try:
            context = await self.llm.astructured_predict(
                ContextArtifact,
                self.new_trip_prompt,
                query=query
            )
            self._log_verbose(f"Step - ContextExtractionAgent: Context extraction successful: {context}")

            return ContextExtractionEvent(
                context=context
            )
        
        except Exception as e:
            self._log_verbose(f"Error extracting context: {str(e)}")
            return StopEvent( 
                result={
                    "status": "error",
                    "message": "Could not understand the travel request. Please try again."
                }
            )

    async def update_context(
        self,
        current_context: ContextArtifact,
        query: str,
        update_target: str
    ) -> Union[ContextExtractionEvent, StopEvent]:
        """Update existing context with new information."""
        try:
            updated_context = await self.llm.astructured_predict(
                ContextArtifact,
                self.update_prompt,
                current_context=current_context.model_dump(),
                query=query,
                update_target=update_target
            )
            self._log_verbose(f"Step - ContextExtractionAgent: Context update successful: {updated_context}")
            
            return ContextExtractionEvent(
                context=updated_context
            )
        except Exception as e:
            self._log_verbose(f"Error updating context: {str(e)}")
            return StopEvent(
                result={
                    "status": "error",
                    "message": "Could not update the travel plan. Please try again."
                }
            )