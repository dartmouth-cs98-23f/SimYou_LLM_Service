import pydantic

# Model for the post request used to prompt the agent
class PromptInfo(pydantic.BaseModel):
    senderId: str   # ID of the sender of the request
    recipientId: str    # ID of the recipient of the request
    isRecipientUser: bool   # Boolean value that indicates whether the recipient is a user
    conversationId: str  # ID of the conversation
    content: str   # content of the prompt
    streamResponse: bool   # Boolean value that indicates whether to stream the response

