from pydantic import BaseModel

# model for the post request used to prompt the agent
class Prompt(BaseModel):
    agentID: str
    prompt: str
    