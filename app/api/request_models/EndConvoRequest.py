import pydantic
from typing import List

# ConversationInfo class that inherits from pydantic's BaseModel
class ConversationInfo(pydantic.BaseModel):
    # The unique identifier for the conversation
    conversationId: str
    # A list of all participants involved in the conversation
    participants: List[str]
