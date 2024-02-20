import pydantic

# Model for the post request used to prompt the agent
class PromptInfo(pydantic.BaseModel):
    senderId: str   # sender of request
    recipientId: str    # recipient of request
    isRecipientUser: bool
    conversationId: str
    content: str
    streamResponse: bool
