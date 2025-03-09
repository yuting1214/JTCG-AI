from abc import ABC, abstractmethod
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

class BaseAgent(ABC):
    def __init__(self, llm: OpenAI, verbose: bool = False):
        self.llm = llm
        self.verbose = verbose

    def _log_verbose(self, message: str) -> None:
        if self.verbose:
            print(message)

    @abstractmethod
    async def process(self, *args, **kwargs):
        pass