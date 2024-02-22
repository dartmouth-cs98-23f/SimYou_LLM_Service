import pydantic
from typing import List

# Class for generating avatar information
class GenerateAvatarInfo(pydantic.BaseModel):
    # Unique identifier for the character
    characterId: str
    # Description of the character's appearance
    appearanceDescription: str