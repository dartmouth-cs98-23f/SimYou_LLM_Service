import pydantic

class UserSummaryInfo(pydantic.BaseModel):
    # The unique identifier for the conversation
    userID: str
    # First participant in the conversation
    summary: str