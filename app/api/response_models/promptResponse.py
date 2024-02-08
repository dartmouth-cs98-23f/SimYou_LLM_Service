from pydantic import BaseModel


class PromptResponse(BaseModel):
    response: str