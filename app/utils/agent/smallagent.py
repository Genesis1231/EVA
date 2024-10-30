from config import logger
from typing import Dict, Callable
from functools import lru_cache

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseLanguageModel

from utils.prompt import load_prompt
from utils.agent.models import (
    create_groq_model,
    create_ollama_model,
    create_anthropic_model
)

class SmallAgent:
    """
    A class representing a memory compressor that compresses a list of messages into a single message.
    Attributes:
        _model_selection (str): The name of the selected language model.
        model_temperature (float): The temperature parameter for generating responses.
        model_factory (dict): A dictionary mapping model names to their corresponding creation methods.
        llm: The initialized language model.
    Methods:
        compress_history: Compress a list of messages into a single message.
    """
    
    def __init__(self, model_name: str = "llama", base_url: str = "http://localhost:11434", model_temperature: float = 0.5) -> None:
        self._model_selection: str = model_name.upper() 
        self._base_url: str = base_url
        self.model_temperature: float = model_temperature
        self._llm = None
    
    @property
    def llm(self):
        if self._llm is None:
            self._llm = self._initialize_model()
        return self._llm

    @llm.setter
    def llm(self, value):
        self._llm = value

    def _get_model_factory(self) -> Dict[str, Callable[[], BaseLanguageModel]]:
        return {
            "GROQ" : lambda: create_groq_model("llama-3.1-8b-instant", self.model_temperature),
            "LLAMA" : lambda: create_ollama_model(self._base_url, "llama3.1", self.model_temperature),
            "ANTHROPIC": lambda: create_anthropic_model(self.model_temperature),
        }
 
    def _initialize_model(self)-> BaseLanguageModel:
        model_factory = self._get_model_factory()
        model = model_factory.get(self._model_selection)
        if model is None:
            raise ValueError(f"Error: Model {self._model_selection} is not supported")
        
        return model() 
    
    def generate(self, template: str, **kwarg) -> str:
        """ Generate a response from the language model based on the given template and arguments """

        prompt = PromptTemplate.from_template(load_prompt(template))
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke(kwarg)
            return response
        
        except Exception as e:
            logger.error(f"SmallAgent: Failed to generate response for {template}: {str(e)}")
            return ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_llm'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)