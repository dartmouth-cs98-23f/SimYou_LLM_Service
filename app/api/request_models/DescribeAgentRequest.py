import pydantic
from typing import List

class InitAgentInfo(pydantic.BaseModel):
    characterId: str
    questions: List[str]
    answers: List[str]