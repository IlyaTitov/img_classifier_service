from pydantic import BaseModel
import uuid


class Detection(BaseModel):
    id: uuid
    image_id: uuid
    object_id: uuid
    y_min
