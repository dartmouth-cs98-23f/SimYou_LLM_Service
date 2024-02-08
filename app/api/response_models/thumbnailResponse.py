import pydantic

class ThumbnailResponse(pydantic.BaseModel):
    thumbnailURL: str