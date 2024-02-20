import pydantic

class AvatarResponse(pydantic.BaseModel):
    avatarURL: str
    headshotURL: str