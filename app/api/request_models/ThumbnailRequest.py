import pydantic
from typing import List

# Model for the post request used to generate thumbnails for worlds
class ThumbnailInfo(pydantic.BaseModel):
    worldID: str
    creatorId: str
    description: str