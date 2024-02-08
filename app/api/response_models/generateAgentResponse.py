from pydantic import BaseModel


class AgentDescriptionModel(BaseModel):
    description: str
    