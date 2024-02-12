import pydantic

# Model for the post request used to prompt the agent to generate a question
class QuestionInfo(pydantic.BaseModel):
    senderId: str   # sender of request
    recipientId: str    # recipient of request
    conversationId: str
    streamResponse: bool