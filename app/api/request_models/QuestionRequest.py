import pydantic

# Model for the post request used to prompt the agent to generate a question
class QuestionInfo(pydantic.BaseModel):
    senderId: str  # The unique identifier for the sender of the request
    recipientId: str  # The unique identifier for the recipient of the request
    isRecipientUser: bool  # Boolean value indicating whether the recipient is a user or not
    conversationId: str  # The unique identifier for the conversation in which the request is made
    streamResponse: bool  # Boolean value indicating whether the response should be streamed or not