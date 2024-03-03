import pydantic
from typing import List

# Pydantic model for initializing an agent
class InitAgentInfo(pydantic.BaseModel):
    name: str  # name of the character
    questions: List[str]  # List of characterizing questions for the agent 
    answers: List[List[str]]  # Corresponding list of answers for the agent
