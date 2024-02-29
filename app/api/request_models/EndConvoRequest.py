import pydantic
from typing import List

# ConversationInfo class that inherits from pydantic's BaseModel
class ConversationInfo(pydantic.BaseModel):
    # The unique identifier for the conversation
    conversationId: str
    # First participant in the conversation
    participantA: str
    # Second participant in the conversation
    participantB: str
    # Is participant A a user
    isParticipantUserA: bool
    # I participant B a user
    isParticipantUserB: bool

