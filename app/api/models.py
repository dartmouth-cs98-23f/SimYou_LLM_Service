import pydantic

# Model for the post request used to prompt the agent
class Prompt(pydantic.BaseModel):
    sourceAgentID: str
    targetAgentID: str
    prompt: str
    msgID=""
    responseID=""

# Model for the post request used to generate thumbnails for worlds
class ThumbnailInfo(pydantic.BaseModel):
    worldID: str
    ownerID: str
    description: str

# Agent info object
class AgentInfo:
    firstName: str
    lastName: str
    description: str

    def __init__(self, firstName, lastName, description):
        self.firstName = firstName
        self.lastName = lastName
        self.description = description
    