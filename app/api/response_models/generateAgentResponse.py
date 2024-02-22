from pydantic import BaseModel

# Model for agent description
class AgentDescriptionModel(BaseModel):
    description: str  # Description of the agent generated with AI