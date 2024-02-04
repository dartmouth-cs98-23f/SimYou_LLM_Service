import pydantic
from types import List

# Model for the post request used to prompt the agent
class Prompt(pydantic.BaseModel):
    questionerID: str
    responderID: str
    msg: str
    respondWithQuestion: bool
    streamResponse: bool
    msgID=""
    responseID=""
    convoID=""

# Agent info object
class AgentInfo:
    firstName: str
    lastName: str
    description: str

    def __init__(self, firstName, lastName, description):
        self.firstName = firstName
        self.lastName = lastName
        self.description = description

class ConversationInfo(pydantic.BaseModel):
    participant1ID: str
    participant2ID: str
    conversationID: str

class InfoToInitAgent(pydantic.BaseModel):
    agentID: str
    questions: List[str]
    answers: List[List[str]]

class ThumbnailInfo(pydantic.BaseModel):
    worldID: str
    description: str



