from pydantic import BaseModel

# Model for a response from prompt to an agent
class PromptResponse(BaseModel):
    response: str # The response string