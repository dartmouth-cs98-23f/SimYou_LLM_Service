from typing import List
from pydantic import BaseModel

# potential agent model
class Agent(BaseModel):
    name: str
    age: int
    traits: str
    status: str
    memories: List[str]

# model for the post request used to prompt the agent
class Prompt(BaseModel):
    agentID: str
    prompt: str
    