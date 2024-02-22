import pydantic
from typing import List

# Pydantic model for initializing an agent
class InitAgentInfo(pydantic.BaseModel):
    characterId: str  # Unique identifier for the character
    questions: List[str]  # List of characterizing questions for the agent 
    answers: List[str]  # Corresponding list of answers for the agent
