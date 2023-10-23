from typing import List
from pydantic import BaseModel

class Agent(BaseModel):
    name: str
    age: int
    traits: str
    status: str
    memories: List[str]

class Query(BaseModel):
    agent_id: int
    prompt: str
    