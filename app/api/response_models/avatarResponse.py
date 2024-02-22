import pydantic

# AvatarResponse model that inherits from the BaseModel of pydantic library
class AvatarResponse(pydantic.BaseModel):
    avatarURL: str  # A string data type attribute to store the URL of the avatar
    headshotURL: str  # A string data type attribute to store the URL of the headshot
