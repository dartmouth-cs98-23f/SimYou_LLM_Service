import pydantic
from typing import List

# Model for the post request used to generate thumbnails for worlds
class ThumbnailInfo(pydantic.BaseModel):
    worldID: str # ID of the world that a thumbnail is being generated for
    creatorId: str # ID of the user that created the world
    description: str # Description of the world as given by the user