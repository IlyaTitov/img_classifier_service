from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from datetime import datetime
from .base import Base
from typing import List


class Image(Base):
    __tablename__ = "image"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    detections: Mapped[List["Detection"]] = relationship(
        back_populates="image",
        cascade="all, delete-orphan",
    )

    original_path: Mapped[str] = mapped_column(nullable=False)
    processed_path: Mapped[str] = mapped_column(nullable=False)
