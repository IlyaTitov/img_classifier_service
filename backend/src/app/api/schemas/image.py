import uuid
from pydantic import BaseModel
from datetime import datetime


class Image(BaseModel):
    id: uuid
    name: str
    created_at: datetime
