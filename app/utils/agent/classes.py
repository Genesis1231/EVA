from config import validate_language, logger
from pydantic import BaseModel, Field, create_model
from typing import Any, List, Dict, Type
from functools import lru_cache

class AgentOutput(BaseModel):
    """Base output format for the agent's responses"""
    analysis: str = Field(description="My reflection and analysis")
    strategy: str = Field(description="My response strategy")
    response: str = Field(description="My verbal response")  # Base description
    premeditation: str = Field(description="My predetermined information")
    action: List[Dict[str, Any]] = Field(
        description="The name of the tools I choose to use and the args for input."
    )
    
    @classmethod
    @lru_cache(maxsize=5)
    def with_language(cls, base_language: str, language: str | None) -> Type["AgentOutput"]:
        """Create a new AgentOutput class with language-specific response description"""
        if not base_language:
            raise ValueError("base_language cannot be empty")
            
        language = validate_language(language) or base_language
        
        verbal_language = (
            f"(ONLY IN NATIVE {language.upper()})"
            if language.upper() not in ("ENGLISH", "MULTILINGUAL")
            else ""
        )
        
        # Create a new class with properly annotated field override
        return create_model(
            f"AgentOutput_{language}",
            __base__=(cls,),
            response=(str, Field(description=f"My verbal response {verbal_language}"))
        )

