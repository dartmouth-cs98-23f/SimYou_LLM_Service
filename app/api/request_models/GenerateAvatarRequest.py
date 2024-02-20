import pydantic
from typing import List

class GenerateAvatarInfo(pydantic.BaseModel):
    characterId: str
    appearanceDescription: str