import pydantic

# Model for a response to a world thumbnail generation request
class ThumbnailResponse(pydantic.BaseModel):
    thumbnailURL: str # URL for the world thumbnail image