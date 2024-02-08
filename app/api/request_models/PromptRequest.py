import pydantic
from typing import List

# Model for the post request used to prompt the agent
class PromptInfo(pydantic.BaseModel):
    senderId: str   # sender of request
    recipientId: str    # recipient of request
    conversationId: str
    content: str
    respondWithQuestion: bool
    streamResponse: bool
