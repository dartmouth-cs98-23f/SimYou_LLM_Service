import pydantic
from typing import List

class ConversationInfo(pydantic.BaseModel):
    conversationId: str
    participants: List[str]

