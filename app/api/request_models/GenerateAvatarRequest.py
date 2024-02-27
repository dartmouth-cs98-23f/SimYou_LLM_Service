import pydantic

# Class for generating avatar information
class GenerateAvatarInfo(pydantic.BaseModel):
    # Description of the character's appearance
    appearanceDescription: str